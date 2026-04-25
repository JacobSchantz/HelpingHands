# Paper Manipulator

## Goal

Train the robot arms to manipulate paper — pick up, fold, crumple, flatten, and place sheets of paper.

## Why Paper?

- **Cheap and abundant** — no special objects needed
- **Deformable** — one of the hardest manipulation challenges
- **Visually obvious** — easy to see if the task succeeded
- **Useful** — folding letters, organizing documents, packaging
- **Benchmarks well** — deformable object manipulation is an active research area

## Tasks (in order of difficulty)

### Level 1: Pick and Place
- Pick up a flat sheet of paper from a table
- Move it to a target position
- Release it

### Level 2: Fold in Half
- Pick up a sheet
- Fold it precisely in half
- Place the folded sheet down

### Level 3: Crumple and Toss
- Grab a sheet
- Crumple it into a ball
- Toss it into a bin

### Level 4: Page Turn
- Place hand on a stack of papers
- Grip the top sheet
- Flip it over (like turning a page)

### Level 5: Envelope Stuffing
- Pick up a letter
- Open an envelope with other hand
- Insert letter
- Close envelope

## Challenges Specific to Paper

| Challenge | Why It's Hard |
|-----------|---------------|
| Paper is thin | Gripping without slipping |
| Paper is flexible | Shape changes during manipulation |
| Paper sticks to itself | Static electricity, moisture |
| No rigidity | Can't predict shape after contact |
| Visual occlusion | Paper folds obscure itself |

## Data Collection Strategy

### Setup
- Standardized workspace: white tabletop, consistent lighting
- A4/letter-size printer paper (consistent weight/thickness)
- Marked target zones on the table
- Camera mounted overhead and at 45° angle

### Recording
- 20 demos per task level
- Each demo: reset → perform task → hold final position
- Record at 30fps with joint positions

### Simulation Approach
Since paper is deformable, traditional joint-angle augmentation may not generalize well. Consider:
- **Domain randomization**: vary paper weight, friction, starting position/orientation
- **Soft-body simulation**: use a sim that models paper physics (e.g., SoftGym, PlasticineLab)
- **Multi-camera setup**: capture paper state from multiple angles for better visual feedback

## Success Criteria

| Level | Metric | Target |
|-------|--------|--------|
| 1 | Pick success rate | >80% |
| 2 | Fold alignment error | <1cm from center crease |
| 3 | Crumple compactness + bin accuracy | Ball <5cm diameter, >70% in bin |
| 4 | Page turn without disturbing stack | >60% success |
| 5 | Complete envelope stuffing | >30% success |

## Research Connections

- [SoftGym](https://sites.google.com/view/softgym) — deformable object simulation
- [DexDeform](https://dexdeform.github.io/) — dexterous deformable manipulation
- [FoldingNet](https://github.com/IroriWorld/FoldingNet) — cloth/paper folding
- [DANO](https://dano-folding.github.io/) — deformable object manipulation with differentiable physics

## Next Steps
1. Start with Level 1 (pick and place flat paper)
2. Record 20 teleop demos
3. Train ACT policy on joint positions
4. Evaluate — if >80%, move to Level 2
5. Add camera for visual feedback if joint-only isn't enough
