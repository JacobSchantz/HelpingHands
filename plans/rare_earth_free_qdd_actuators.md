# Rare earth free QDD actuator research and manufacturing plan

Research decision, 2026-10-23. Jake prefers quasi-direct-drive (QDD) joints and wants to manufacture actuators over time, reducing total cost while avoiding rare-earth materials. Start with **La-free ferrite flux-concentrating spoke/IPM and ferrite-assisted synchronous reluctance**, compared against a magnet-free synchronous reluctance design. Keep ferrite Halbach and switched reluctance as secondary candidates. These are priorities for simulation, not demonstrated winners.

No purchases, motor substitutions, CAD changes or new part versions are authorized by this research. RS00, RS06, STS3215 and all existing Mount/Base interfaces remain the prototype baseline. The long-term goal is one small actuator for gripper/wrist and one larger actuator for proximal joints; whether two sizes suffice depends on measured loads.

## What QDD does and does not establish

QDD combines a motor with a low reduction ratio; it does not require permanent magnets. A low ratio can improve backdrivability and reduce reflected rotor inertia, but bearings, gears, seals, cogging and controller behavior still matter. Published robotic QDD work establishes the architecture's usefulness for manipulation, not that a ferrite replacement matches a particular commercial joint. [Berkeley Blue research](https://arxiv.org/abs/1904.03815)

For gear ratio N = motor speed / joint speed and forward efficiency η:

- Joint torque ≈ η N × motor torque; motor speed = N × joint speed.
- Rotor inertia reflected to the joint = N² × rotor inertia. Raising N from 10 to 20 quadruples this contribution before changes in rotor design.
- Mechanical power = torque × angular velocity, with angular velocity = rpm × 2π/60. At zero speed, holding torque consumes electrical power and produces heat while delivering zero mechanical power. Peak kW cannot establish holding performance.

Current is a torque estimate, not a direct force sensor. Reluctance and IPM designs require maps over rotor angle, d/q current and temperature; saturation and gearbox friction complicate the estimate. Validate it against a joint torque transducer before using it for grip force control.

## Existing joint benchmarks

Manufacturer specifications are comparison anchors, not measurements of our hardware. The [B601-RS BOM](https://github.com/Seeed-Projects/reBot-DevArm/blob/main/hardware/reBot_B601_RS/README.md) assigns three RS06 and four RS00, including the gripper motor. The following numbers come from the manufacturer's July 2026 CAN2.0 manuals, sections 1.2–1.4. Do not mix CAN-FD variants or older thermal curves.

| Attribute | RS00 small benchmark | RS06 larger benchmark |
| --- | --- | --- |
| Output rated / peak torque | 5 / 14 N·m | 11 / 36 N·m |
| Rated torque test speed | 100 rpm | 100 rpm |
| No-load output speed | 315 rpm ±10% | 480 rpm ±10% |
| Reduction | 10:1 | 9:1 |
| Integrated mass | 310 g ±3 g | 621 g ±3 g |
| Supply | 48 V nominal, 24–60 V | 48 V nominal, 15–60 V |
| Rated phase current, amplitude | 4.7 A peak | 14.3 A peak |
| Maximum phase current, amplitude | 15.5 A peak | 57 A peak |
| Rated-load heatsink dimensions | 90 × 85 mm | 130 × 160 mm |

Sources: [RS00 manual](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS00/RS00User%20Manual260713.pdf), [RS06 manual](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS06/RS06User%20Manual260713.pdf). RS06's overload section separately specifies 130 × 155 mm, so record the actual fixture when reproducing a test. Both manuals distinguish rotation from stall heating; their rated torque at 100 rpm does **not** certify the same continuous stationary torque. Peak duration depends on starting temperature, cooling and speed; reproduce the selected revision's thermal curves rather than assign one universal duration.

RS00 packaging in the current project is Ø57 × 51 ±1 mm, with the output and rear-face interfaces recorded in [AGENTS.md](../AGENTS.md). Reuse the pinned CAD for the complete envelope, including connectors and output bearing support; extract RS06 dimensions from its drawing/STEP before freezing its comparison envelope. No RS06 envelope is assumed here.

**Proposed comparison targets, not established application requirements:** begin with RS00-class 5 N·m at 100 rpm and 14 N·m transient, at the existing complete-actuator envelope and 310 g mass reference. Report continuous stall torque independently; 5 N·m at stall is an aspirational target until baseline testing. Repeat the method at RS06 scale. Record real arm/gripper duty cycles, external loads, desired grip-force accuracy and permitted surface temperature before declaring either size sufficient. Never pair the no-load maximum speed with peak torque as a simultaneous operating point.

## Evidence and candidate ranking

Confidence here separates demonstrated technology from its applicability to our joint. Priority is engineering judgment based on the evidence below; no equal-envelope robot comparison has been performed.

| Priority and topology | Evidence status | Robot-joint tradeoffs to resolve |
| --- | --- | --- |
| 1A Ferrite spoke or flux-concentrating IPM | ORNL built and tested a ferrite traction motor; high confidence in feasibility, low confidence in RS00-scale equivalence | Concentrating flux may compensate for weaker magnets, but leakage, saturated bridges, rotor retention and magnet volume constrain torque per mass. Test cogging, torque ripple, cold demagnetization and winding hot spots. Complex laminations and magnet insertion raise tooling and assembly costs. |
| 1B Ferrite-assisted synchronous reluctance | Published Elmer study includes simulation and a manufactured/tested prototype; no compact robot duty validation | Combine reluctance and magnet torque. Evaluate saliency, saturation, inverter current and power factor; low-speed force control needs calibrated maps. Barrier geometry and ferrite insertion must remain manufacturable. |
| 2 Magnet-free synchronous reluctance | Commercial industrial motors establish the topology, not compact QDD performance | Removes motor magnets and their demagnetization risk. Magnetizing current competes with torque current under a fixed inverter limit; rotor barriers, torque ripple and torque density need comparison. Encoder-based control is the starting assumption at standstill. |
| 3 Ferrite Halbach PM | Flux arrangement worth simulating; no verified RE-free robot actuator benchmark in reviewed leads | Segmented orientation and assembly fixtures add cost; weaker ferrite flux is not automatically recovered by an array. Check retention, leakage, thermal path, ripple and total magnet mass. |
| 4 Switched reluctance | Established motor family; not interchangeable with a synchronous motor/controller | Simple magnet-free rotor and concentrated coils may simplify fabrication. Angle-dependent torque, saturation, acoustic noise, radial forces and ripple increase control/testing work. Include phase converter development and sensing in the BOM. |

The [ORNL FY2015 report, printed pp. 12–16](https://info.ornl.gov/sites/publications/files/Pub59624.pdf) explains lower ferrite remanence/coercivity, greater magnet-volume needs and electromagnetic design constraints. Its materials discussion does not certify the proposed supplier's magnets as La-free. The [2017 DOE/ORNL review, slide 7](https://www.energy.gov/sites/default/files/2017/06/f34/edt074_burress_2017_o.pdf) reports a built ferrite motor reaching **103 kW peak**. This is traction evidence, not continuous joint torque, stall temperature, backdrive torque or a robot actuator BOM.

The [2022 ferrite-assisted SynRM paper](https://dgjsxb.ces-transaction.com/EN/abstract/abstract7518.shtml) reports simulation comparisons plus measured prototype power/efficiency maps. Its abstract does not establish our mass, envelope, stall duty or an openly licensed manufacturing package. [ABB's commercial SynRM range](https://www.abb.com/global/en/areas/motion/motors-generators/low-voltage-motors/iec-low-voltage-motors/synchronous-reluctance-motors) supports magnet-free motor feasibility at industrial scale. Neither establishes our ranking quantitatively.

Across every candidate, rank measured continuous torque and continuous stall torque first, followed by timed peak torque, loaded speed, total actuator mass/envelope, backdrive torque/hysteresis, ripple and low-speed tracking. Then compare temperature-dependent material margin and complete manufacturing cost. A higher peak torque alone cannot win.

## Material definition and open design reuse

Require explicitly **La-free strontium ferrite**, with supplier composition declaration, batch traceability and demagnetization curves across the intended temperature/current range. Ferrite is not automatically rare-earth-free: [TDK's ferrite guide, pp. 2–3](https://product.tdk.com/de/system/files?file=dam/doc/product/magnet/magnet/ferrite/datasheets/magnet_fb_summary_en.pdf) distinguishes La-Co-added and La-Co-free material classes. Cold as well as hot conditions need checking against the selected grade's curves. Cobalt is not a rare earth, although cost and supply still matter. Heavy-rare-earth-free NdFeB still contains rare earths.

For a **whole-actuator** RE-free claim, also audit encoder magnets, brakes, adhesives/fillers and purchased subassemblies. An optical or inductive encoder is an option if magnetic encoder composition cannot be certified. Define whether the requirement covers functional bulk materials or trace contamination; a magnet marketing label is insufficient.

| Resource | Verified reuse scope and license | Missing before production reuse |
| --- | --- | --- |
| [SyR-e](https://github.com/SyR-e/syre_public) | Apache-2.0 MATLAB electrical-machine design and drive simulation, with motor examples | MATLAB dependency; it is not a fully free toolchain or released robot actuator. Pin a revision and audit included examples/dependencies. |
| [Elmer](https://github.com/ElmerCSC/elmerfem) | Open multiphysics solver; [CSC documents GPL and solver-library LGPL licensing](https://docs.csc.fi/apps/elmer/) | Validate electromagnetic and thermal models, materials and module-specific licenses. A published Elmer workflow is not the paper's manufacturing files. |
| [ODRI actuator hardware](https://github.com/open-dynamic-robot-initiative/open_robot_actuator_hardware) | BSD-3-Clause mechanical/electronics references and assembly/test instructions | Useful assembly/control foundation; purchased motor materials are not verified RE-free. Its mechanics are not an RS00 drop-in. |
| [moteus](https://github.com/mjbots/moteus) | Apache-2.0 by default, with stated exceptions; PCB and brushless servo firmware sources | Check board current, cooling and regeneration limits. Current boards have differing voltage limits, none should be assumed compatible with a 60 V bus. SynRM torque maps/control need work; SRM may need a different power stage. |
| [Ironless QDD](https://github.com/CKraft11/Ironless-QDD-Actuator) | CAD, FEMM, BOM and controller configuration listed; README declares MIT, but no separate license file was found in the current tree | [Author's construction report](https://cadenkraft.com/ironless-cycloidal-planetary-actuator/) specifies N52/N50 magnets: fails our material goal. Confirm complete license notice and LFS assets before reuse. Its holding-torque claims are not thermal-equilibrium ratings. |

No complete, proven, openly licensed RE-free QDD actuator was identified in these reviewed leads. This is a bounded finding, not a claim that none exists. Cybercab ferrite Halbach architecture remains unverified here and is not a design basis. A Halbach arrangement is neither a material specification nor an open-source design.

## Manufacturing roadmap

Each stage below is proposed future work and produces evidence before the next commitment.

1. **Establish the job and baseline.** Record RS00/RS06 torque, speed, bus current, temperatures, backdrive and duty cycles in the actual mounting/cooling arrangement. Define force-control accuracy and permissible envelope growth. Measure standalone motor and complete joint effects separately where practical.
2. **Compare equal constraints in simulation.** Model 1A, 1B and magnet-free SynRM first, with an NdFeB reference for calibration. Hold total envelope, winding temperature limit, bus voltage, phase-current convention/limit, cooling boundary and gear ratio constant. Include end turns, inverter/encoder space and gear/bearing mass. Keep a separate relaxed-envelope result rather than quietly growing the ferrite candidate. Use measured lamination B-H/loss data and supplier magnet curves. Sweep rotor angle and d/q currents through saturation, short peaks and demagnetizing fault currents. Include thermal contact resistance, copper/core/inverter losses, inertia, voltage headroom and manufacturing tolerances. Check mesh/time-step convergence and 2D end-effect assumptions before trusting rankings.
3. **Design one bench motor.** Prefer purchased certified magnets, electrical steel, insulated copper winding wire, bearings and controller for the first prototype. Outsource laser-cut insulated laminations and critical shaft/rotor machining; inspect burrs, interlaminar shorts, concentricity and airgap. Wind with documented turns/tension/insulation, impregnate, retain brittle ferrites mechanically and balance the rotor. Printed fixtures and noncritical housings help iteration; the motor's thermal and precision paths need suitable materials. Do not combine a new topology, homemade ferrite and experimental aluminium insulation in the first experiment.
4. **Validate on a dynamometer before an arm.** Couple through a calibrated torque transducer to a controllable load; instrument phase currents, DC voltage/current, encoder angle and winding/housing temperatures. Provide overspeed containment, current/thermal limits, emergency stop and regeneration handling appropriate to the fixture. Use the same cooling and initial temperatures as the commercial reference.
5. **Pilot complete actuators.** After passing motor tests, integrate one low-ratio stage and the shared mechanical/electrical interface, then validate bearing loads, backlash, seals, cable clearance, CAN behavior, grip-force estimates and endurance. Produce drawings/tolerances, winding and assembly fixtures, calibration firmware and traceable end-of-line records. Only then evaluate a production cell.
6. **Bring processes inside selectively.** Start with winding, assembly, calibration and testing; contract laminations, gears, bearings, magnets and PCBs until yield/cost justify more. Volume may justify lamination stamping dies, ferrite pressing/sintering/magnetizing and automated winding. Making ferrite from raw feedstock adds powder processing, atmosphere/temperature control, shrinkage, orientation, grinding and magnetic metrology. Owning the actuator design does not require owning every materials process. Validate robot assembly cycle time and yield before claiming the factory can reproduce its actuator supply.

## Proposed dynamometer acceptance record

These test settings are planning assumptions to refine against baseline data, not measured results or approved product requirements.

| Test | Record and proposed decision rule |
| --- | --- |
| Continuous rotation and stall | Measure at 0, 1, 10 and 100 output rpm in both directions, including worst electrical holding angles. Define equilibrium as temperature slope below 0.1 °C/min for 30 minutes without exceeding the selected material/component limits; stop at a predeclared duration if equilibrium is not reached and mark inconclusive. Report steady torque separately at each speed. |
| Peak torque duration | At cold start and warmed equilibrium, record torque/current/temperature for 1, 5 and 10 s pulses within simulation limits, plus the required recovery interval. Do not start by assuming 14 or 36 N·m is safe for the new motor. |
| Efficiency | Map DC input to measured shaft output through the speed/torque range, including inverter and gearbox losses. At stall report watts and temperature, not a misleading efficiency percentage. |
| Ripple and low-speed control | Record peak-to-peak and RMS torque ripple, tracking error and torque-estimate error across rotor angles, current and temperature; state measurement bandwidth and sampling. Compare loaded bidirectional 0–1 rpm motion and static force holds. |
| Backdrive and mechanics | Measure breakaway and running torque versus angle/speed in both directions, unpowered open-phase and powered zero-torque modes. Separate intentionally shorted braking behavior. Report hysteresis, backlash, bearing load capacity and reflected inertia. |
| Demagnetization and life | Compare flux/back-EMF and torque maps before/after temperature and current excursions within the supplier envelope; inspect retention, insulation and gears. Magnet-free candidates still require thermal/insulation endurance tests. |

Advance only if the chosen size meets the actual duty-cycle torque/speed and force-control error limits, and its quoted total cost justifies its mass/envelope and development cost. If no candidate passes the fixed envelope, explicitly choose between more space, more cooling, reduced performance or keeping the commercial prototype. Raising gearing is a separately reported compromise.

## Parameterized cost comparison

Compare **finished, tested actuators with equivalent duty**, not raw magnets against a retail module. As a dated purchase reference only, [Seeed lists RS00 at $138.99 and $131.99 for 10+](https://www.seeedstudio.com/Robostride-00-Actuator-p-6664.html) on 2026-10-23, before freight/tax. This is neither a volume quote nor a rare-earth-free product. Obtain a like-for-like RS06 quote and vendor warranty/support terms separately.

Use scenarios of **10 prototypes, 1,000/year, 100,000/year and 10 million/year**; the latter is a scale aspiration, not a forecast. Tool amortization uses committed lifetime good units, not annual capacity. Every blank below means **unknown**, never zero. No supplier prices or percentage savings are assumed.

| Cost input per candidate | Low volume basis | Volume basis |
| --- | --- | --- |
| Laminations, rotor and certified magnets or magnet-free rotor | Laser-cut/setup quote, actual material yield, rotor machining | Stamping tool life/cavities, steel utilization, magnet tooling/MOQ and supplier yield |
| Windings and insulation | Wire, bobbins, varnish, manual minutes | Winding/termination automation, consumables, machine cycle and maintenance |
| Transmission and bearings | Purchased gears/stage, shafts, bearings, lubricant | Production gear process, tolerances, inspection, supplier contracts |
| Housing and thermal path | Machining/printing hours, inserts, thermal interfaces | Casting/molding/machining tools, thermal qualification and amortization |
| Electronics and sensing | PCB assembly, FETs, MCU, gate drivers, current/temperature sensors, encoder, connectors, cables | Quoted PCBA volumes, test/program/calibration time, RE-free sensing and approved alternates |
| Assembly and quality | Loaded labor rate × timed minutes, fixture/test allocation, scrap/rework | Automation capex/uptime, operator time, first-pass/final yield, endurance sampling |
| Product delivery | Packaging, freight/duty, warranty reserve, support | Same scope with quoted logistics and field-failure assumptions |
| Nonrecurring engineering | Motor/control design, simulation/tool licenses, prototypes and test stand | Additional production engineering, qualification, factory/tooling capex |

For each topology and volume scenario define B = material/component/outsourced-process cost per started unit; A = assembly and test labor/machine cost per start; Y = final good-unit yield; R = expected rework cost per start; W = warranty/support/packaging/logistics per good unit; F = allocated tooling and nonrecurring engineering; Q = lifetime good units over which F is amortized. Then:

**Own cost per good unit = (B + A + R) / Y + W + F / Q.**

Quote common items once and retain topology-specific deltas: PM ferrite/retention versus SynRM barrier fabrication/inverter current versus SRM converter/control work. Add factory energy and equipment maintenance to A; include scrap salvage credits in B if supported. Compare with delivered purchased-module cost plus integration/support on the same accounting basis. A small magnet saving can be overwhelmed by gearing, encoder, inverter, labor or rejected units.

Break-even lifetime quantity is **F / (delivered buy cost − own recurring good-unit cost)** only when the denominator is positive and demand, yield and tool life support that quantity. Run low/base/high quote ranges for yield, labor minutes, tooling utilization, cooling mass, winding fill, gear life and controller current. Vary magnet price while holding other cost inputs constant to bound what the magnet line alone could save. Until these inputs are quoted and performance passes, “drastically cheaper” remains the goal, not a result.

The next concrete deliverable is an equal-constraint simulation comparison plus a baseline dynamometer test specification. Hardware fabrication and production investment require a later decision using those results.
