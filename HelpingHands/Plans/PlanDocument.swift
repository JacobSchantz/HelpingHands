import Foundation

/// One spoken unit of a plan. Narration moves a step at a time so "next",
/// "back" and "repeat" always land somewhere a listener can follow, and so a
/// paused plan can be resumed on a sentence boundary instead of mid-word.
struct PlanStep: Identifiable, Hashable {
    enum Kind: String, Hashable {
        case heading
        case paragraph
        case item
        case tableRow
        case note
    }

    var id: Int
    var kind: Kind
    /// The heading this step sits under ("" before the first heading).
    var section: String
    /// What the synthesizer says (may carry spoken-only scaffolding).
    var spoken: String
    /// What the screen shows.
    var display: String
}

/// A plan the app can read aloud: a markdown file from `plans/`, a file the
/// user imported, or text they pasted in.
struct PlanDocument: Identifiable, Hashable {
    enum Origin: Hashable {
        case bundled
        case imported
    }

    var id: String
    var title: String
    /// Where it came from, e.g. "plans/tool_caddy.md" or "Pasted".
    var source: String
    var origin: Origin
    var url: URL?
    var steps: [PlanStep]

    /// Headings in reading order — the spoken table of contents.
    var sections: [String] {
        var seen = Set<String>()
        return steps
            .filter { $0.kind == .heading }
            .map(\.display)
            .filter { seen.insert($0).inserted }
    }

    var wordCount: Int {
        steps.reduce(0) { $0 + $1.spoken.split(separator: " ").count }
    }

    /// Rough listening time: the default voice lands near 155 words a minute.
    var spokenMinutes: Int {
        max(1, Int((Double(wordCount) / 155.0).rounded()))
    }

    var summaryLine: String {
        "\(steps.count) steps · about \(spokenMinutes) min"
    }

    static func parse(markdown: String,
                      id: String,
                      fallbackTitle: String,
                      source: String,
                      origin: Origin,
                      url: URL?) -> PlanDocument {
        let parsed = PlanMarkdown.parse(markdown)
        return PlanDocument(
            id: id,
            title: parsed.title ?? fallbackTitle,
            source: source,
            origin: origin,
            url: url,
            steps: parsed.steps)
    }
}

/// Turns a markdown plan into speakable steps.
///
/// This is deliberately a hand-rolled line scanner rather than a full markdown
/// parser: what matters for listening is the *shape* (headings, list items,
/// table rows, paragraphs), and everything that only makes sense visually —
/// code fences, rules, badges — has to be summarised or dropped so the ear
/// never hears punctuation soup.
enum PlanMarkdown {
    static func parse(_ markdown: String) -> (title: String?, steps: [PlanStep]) {
        var steps: [PlanStep] = []
        var title: String?
        var section = ""
        var paragraph: [String] = []
        var table: [[String]] = []
        var openItem: Int?
        var inCode = false
        var codeLines = 0

        func add(_ kind: PlanStep.Kind, spoken: String, display: String) {
            let shown = display.trimmingCharacters(in: .whitespacesAndNewlines)
            let said = spoken.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !shown.isEmpty, !said.isEmpty else { return }
            steps.append(PlanStep(id: steps.count, kind: kind, section: section,
                                  spoken: said, display: shown))
        }

        func flushParagraph() {
            guard !paragraph.isEmpty else { return }
            let text = inline(paragraph.joined(separator: " "))
            paragraph.removeAll()
            add(.paragraph, spoken: text, display: text)
        }

        func flushTable() {
            guard !table.isEmpty else { return }
            let rows = table
            table.removeAll()

            let isSeparator: ([String]) -> Bool = { cells in
                !cells.isEmpty && cells.allSatisfy { cell in
                    let trimmed = cell.trimmingCharacters(in: CharacterSet(charactersIn: ": "))
                    return !trimmed.isEmpty && trimmed.allSatisfy { $0 == "-" || $0 == "=" }
                }
            }

            var header: [String] = []
            var body: [[String]] = []
            for (offset, row) in rows.enumerated() {
                if isSeparator(row) {
                    if offset == 1, let first = rows.first { header = first }
                    continue
                }
                if offset == 0 && rows.count > 1 && isSeparator(rows[1]) { continue }
                body.append(row)
            }

            for row in body {
                let pairs = row.enumerated().map { index, cell -> String in
                    let label = index < header.count ? inline(header[index]) : ""
                    let value = inline(cell)
                    return label.isEmpty ? value : "\(label): \(value)"
                }.filter { !$0.isEmpty }
                let line = pairs.joined(separator: ", ")
                add(.tableRow, spoken: line + ".", display: line)
            }
        }

        func flushBlocks() {
            flushTable()
            flushParagraph()
            openItem = nil
        }

        for rawLine in markdown.components(separatedBy: .newlines) {
            let line = rawLine.trimmingCharacters(in: .whitespaces)

            if line.hasPrefix("```") || line.hasPrefix("~~~") {
                if inCode {
                    inCode = false
                    add(.note,
                        spoken: "Code block, \(codeLines) \(codeLines == 1 ? "line" : "lines"). Skipping it.",
                        display: "Code block (\(codeLines) \(codeLines == 1 ? "line" : "lines")) — not read aloud")
                    codeLines = 0
                } else {
                    flushBlocks()
                    inCode = true
                    codeLines = 0
                }
                continue
            }
            if inCode {
                codeLines += 1
                continue
            }

            if line.isEmpty {
                flushBlocks()
                continue
            }

            if line.hasPrefix("|") {
                flushParagraph()
                openItem = nil
                table.append(cells(in: line))
                continue
            }
            flushTable()

            if isRule(line) {
                flushBlocks()
                continue
            }

            let body = line.hasPrefix(">")
                ? String(line.dropFirst()).trimmingCharacters(in: .whitespaces)
                : line

            if let heading = heading(in: body) {
                flushBlocks()
                let text = inline(heading.text)
                guard !text.isEmpty else { continue }
                if heading.level == 1 && title == nil {
                    title = text
                }
                section = text
                let spoken: String
                switch heading.level {
                case 1: spoken = "\(text)."
                case 2: spoken = "Section: \(text)."
                default: spoken = "\(text)."
                }
                add(.heading, spoken: spoken, display: text)
                continue
            }

            if let item = listItem(in: body) {
                flushParagraph()
                let text = inline(item.text)
                guard !text.isEmpty else { continue }
                var spoken = text
                var display = text
                if let number = item.number {
                    spoken = "\(number). \(text)"
                    display = "\(number). \(text)"
                }
                if let done = item.checked {
                    spoken = (done ? "Done. " : "To do. ") + spoken
                    display = (done ? "☑︎ " : "☐ ") + display
                }
                add(.item, spoken: spoken, display: display)
                openItem = steps.count - 1
                continue
            }

            // A plain line: either the continuation of the list item above it
            // or part of the paragraph being gathered.
            if let open = openItem, paragraph.isEmpty {
                let text = inline(body)
                steps[open].spoken += " " + text
                steps[open].display += " " + text
                continue
            }
            paragraph.append(body)
        }

        flushBlocks()
        return (title, steps)
    }

    // MARK: - Line shapes

    private static func heading(in line: String) -> (level: Int, text: String)? {
        guard line.hasPrefix("#") else { return nil }
        let level = line.prefix(while: { $0 == "#" }).count
        guard level <= 6 else { return nil }
        let rest = String(line.dropFirst(level))
        guard rest.hasPrefix(" ") || rest.isEmpty else { return nil }
        return (level, rest.trimmingCharacters(in: .whitespaces))
    }

    private static func listItem(in line: String) -> (number: Int?, checked: Bool?, text: String)? {
        var rest: String
        var number: Int?

        if let first = line.first, "-*+".contains(first) {
            let after = line.dropFirst()
            guard after.hasPrefix(" ") else { return nil }
            rest = String(after).trimmingCharacters(in: .whitespaces)
        } else {
            let digits = line.prefix(while: \.isNumber)
            guard !digits.isEmpty, digits.count <= 3 else { return nil }
            let after = line.dropFirst(digits.count)
            guard let marker = after.first, marker == "." || marker == ")" else { return nil }
            let text = after.dropFirst()
            guard text.hasPrefix(" ") else { return nil }
            number = Int(digits)
            rest = String(text).trimmingCharacters(in: .whitespaces)
        }

        var checked: Bool?
        let lowered = rest.lowercased()
        if lowered.hasPrefix("[ ] ") {
            checked = false
            rest = String(rest.dropFirst(4))
        } else if lowered.hasPrefix("[x] ") {
            checked = true
            rest = String(rest.dropFirst(4))
        }
        return (number, checked, rest)
    }

    private static func isRule(_ line: String) -> Bool {
        guard line.count >= 3 else { return false }
        let set = Set(line)
        return set.count == 1 && (set.first == "-" || set.first == "*" || set.first == "_" || set.first == "=")
    }

    private static func cells(in row: String) -> [String] {
        var trimmed = row
        if trimmed.hasPrefix("|") { trimmed.removeFirst() }
        if trimmed.hasSuffix("|") { trimmed.removeLast() }
        return trimmed.components(separatedBy: "|").map { $0.trimmingCharacters(in: .whitespaces) }
    }

    /// Strips the markup a listener can't hear: links keep their text, images
    /// keep their alt text, and emphasis/code ticks go away entirely.
    static func inline(_ text: String) -> String {
        var out = ""
        var index = text.startIndex

        while index < text.endIndex {
            let character = text[index]

            if character == "!" || character == "[" {
                var cursor = index
                if character == "!" {
                    cursor = text.index(after: cursor)
                    guard cursor < text.endIndex, text[cursor] == "[" else {
                        out.append(character)
                        index = text.index(after: index)
                        continue
                    }
                }
                if let close = text[cursor...].firstIndex(of: "]") {
                    let label = String(text[text.index(after: cursor)..<close])
                    var after = text.index(after: close)
                    if after < text.endIndex, text[after] == "(" ,
                       let paren = text[after...].firstIndex(of: ")") {
                        after = text.index(after: paren)
                    }
                    out += label
                    index = after
                    continue
                }
            }

            if character == "*" || character == "`" || character == "~" {
                index = text.index(after: index)
                continue
            }

            if character == "<", let close = text[index...].firstIndex(of: ">"),
               text[text.index(after: index)..<close].allSatisfy({ !$0.isWhitespace }) {
                index = text.index(after: close)
                continue
            }

            out.append(character)
            index = text.index(after: index)
        }

        return out
            .components(separatedBy: .whitespacesAndNewlines)
            .filter { !$0.isEmpty }
            .joined(separator: " ")
    }
}
