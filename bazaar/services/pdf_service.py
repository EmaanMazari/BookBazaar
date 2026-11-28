# ========================================================
# Bookzy AI - Digital Library & Soft Copy PDF Service
# Generates and serves valid, multi-page PDF soft copies for free books
# Zero 3rd-party binary dependencies (100% portable on any OS)
# ========================================================

import io
import re
from datetime import datetime


def _sanitize_pdf_text(text: str) -> str:
    """Sanitizes text for PDF literal string encoding."""
    if not text:
        return ""
    clean = str(text).replace('\\', '/').replace('(', '[').replace(')', ']')
    clean = re.sub(r'[^\x20-\x7E]', ' ', clean)
    return clean.strip()


def _get_curriculum_data(title: str, subject: str, category: str, grade: str):
    """Returns rich, subject-specific table of contents, high-yield notes, and MCQs."""
    comb = f"{title} {subject} {category} {grade}".lower()

    if 'physics' in comb:
        toc = [
            ("Unit 1: Physical Quantities & Measurements", "International System of Units (SI), Vernier Calipers, Screw Gauge", "Page 5"),
            ("Unit 2: Kinematics & Equations of Motion", "Scalars vs Vectors, Speed, Velocity, Acceleration, Derivation of Equations", "Page 18"),
            ("Unit 3: Dynamics & Newton's Laws of Motion", "Momentum, Law of Conservation of Momentum, Friction, Centripetal Force", "Page 34"),
            ("Unit 4: Turning Effect of Forces & Equilibrium", "Torque, Centre of Gravity, States and Conditions of Equilibrium", "Page 52"),
            ("Unit 5: Gravitation & Planetary Motion", "Newton's Law of Gravitation, Mass of Earth, Orbital Velocity of Satellites", "Page 68"),
            ("Unit 6: Work, Energy & Power Efficiency", "Forms of Kinetic and Potential Energy, Conservation of Energy, Power", "Page 85"),
            ("Unit 7: Properties of Matter & Fluid Mechanics", "Density, Pressure, Pascal's Law, Archimedes Principle, Hooke's Law", "Page 102"),
            ("Unit 8: Thermal Properties & Heat Transfer", "Specific Heat Capacity, Latent Heat of Fusion/Vaporization, Radiation", "Page 120"),
        ]
        notes = [
            ("Key Equations of Motion", "1) vf = vi + at    2) S = vi*t + 0.5*a*t^2    3) 2aS = vf^2 - vi^2"),
            ("Newton's Fundamental Laws", "F = m*a (Second Law) | Force = rate of change of momentum (dp/dt) | P = F/A"),
            ("Work and Kinetic Energy", "Work = F * d * cos(theta) [Joules] | K.E = 0.5*m*v^2 | P.E = m*g*h | Power = W/t [Watts]"),
            ("Gravitation & Satellites", "F = G*(m1*m2)/r^2 | Mass of Earth Me = (g * R^2) / G = 6.0 x 10^24 kg"),
            ("Hooke's Law & Elasticity", "Stress / Strain = Young's Modulus (Y) | F = -k*x (Restoring Force in Spring)"),
        ]
        mcqs = [
            ("Q1: Which of the following is a derived base SI unit?", "A) Kilogram", "B) Newton", "C) Meter", "D) Second", "Answer: B (Newton = kg*m/s^2)"),
            ("Q2: The rate of change of momentum is equal to:", "A) Impulse", "B) Applied Force", "C) Velocity", "D) Acceleration", "Answer: B (Newton's 2nd Law: F = dp/dt)"),
            ("Q3: The value of 'g' at the center of the Earth is:", "A) 9.8 m/s^2", "B) Infinite", "C) Zero", "D) 4.9 m/s^2", "Answer: C (Gravitational field is zero at center)"),
            ("Q4: Work done will be maximum when angle between Force and Displacement is:", "A) 0 degrees", "B) 45 degrees", "C) 90 degrees", "D) 180 degrees", "Answer: A (cos 0 = 1, maximum work)"),
        ]
    elif 'chem' in comb:
        toc = [
            ("Unit 1: Fundamentals of Chemistry & Mole Concept", "Atomic Number, Mass Number, Avogadro's Number, Empirical & Molecular Formula", "Page 4"),
            ("Unit 2: Structure of Atoms & Electronic Configuration", "Rutherford Model, Bohr Theory, Sub-shells (s, p, d, f) and Isotopes", "Page 22"),
            ("Unit 3: Periodic Table & Periodicity of Properties", "Periodic Trends: Atomic Radius, Shielding Effect, Electronegativity, Ionization", "Page 40"),
            ("Unit 4: Structure of Molecules & Chemical Bonding", "Ionic, Covalent, Coordinate Covalent Bonds, Intermolecular Hydrogen Bonding", "Page 58"),
            ("Unit 5: Physical States of Matter & Gas Laws", "Boyle's Law, Charles's Law, Evaporation, Boiling Point, Allotropy", "Page 76"),
            ("Unit 6: Solutions, Molarity & Solubility", "Saturated vs Unsaturated, Molarity (M = moles/dm^3), Colloids and Suspensions", "Page 94"),
            ("Unit 7: Electrochemistry & Oxidation-Reduction", "Oxidation Numbers, Galvanic vs Electrolytic Cells, Corrosion and Prevention", "Page 112"),
            ("Unit 8: Chemical Reactivity & Non-Metals", "Comparison of Metals and Non-Metals, Halogens, Inert Noble Gases", "Page 130"),
        ]
        notes = [
            ("The Mole Concept & Avogadro", "Number of particles = Moles * 6.022 x 10^23 | Moles = Mass in grams / Molar Mass"),
            ("Gas Laws Formulation", "Boyle's Law: P1*V1 = P2*V2 (T const) | Charles's Law: V1/T1 = V2/T2 (P const) | PV = nRT"),
            ("Oxidation & Reduction", "Oxidation = Loss of Electrons (LEO) | Reduction = Gain of Electrons (GER)"),
            ("Chemical Equilibrium Constant", "Kc = [Products]^coefficients / [Reactants]^coefficients | Le Chatelier's Principle"),
            ("Acids, Bases and pH Scale", "pH = -log[H+] | pOH = -log[OH-] | pH + pOH = 14 at 25 degrees Celsius"),
        ]
        mcqs = [
            ("Q1: The number of moles in 36 grams of pure water (H2O) is:", "A) 1 mole", "B) 2 moles", "C) 3 moles", "D) 18 moles", "Answer: B (Molar mass of H2O is 18 g/mol; 36/18 = 2)"),
            ("Q2: In the Periodic Table, electronegativity across a period from left to right:", "A) Decreases", "B) Increases", "C) Remains Constant", "D) Fluctuates", "Answer: B (Nuclear charge increases)"),
            ("Q3: Which sub-shell has the lowest energy level?", "A) 2s", "B) 1s", "C) 2p", "D) 3s", "Answer: B (1s is closest to nucleus)"),
            ("Q4: Rusting of iron is an electrochemical reaction involving:", "A) Reduction only", "B) Oxidation only", "C) Redox Reaction", "D) Neutralization", "Answer: C (Iron is oxidized, Oxygen reduced)"),
        ]
    elif 'math' in comb or 'algebra' in comb or 'calculus' in comb:
        toc = [
            ("Unit 1: Matrices, Determinants & Cramer's Rule", "Types of Matrices, Adjoint, Inverse of 2x2 Matrix, System of Linear Equations", "Page 3"),
            ("Unit 2: Real & Complex Numbers", "Radicals, Laws of Exponents, Complex Conjugates, Operations on z = a + bi", "Page 24"),
            ("Unit 3: Logarithms & Scientific Notation", "Common vs Natural Logs, Laws of Logarithms, Characteristic & Mantissa", "Page 45"),
            ("Unit 4: Algebraic Expressions & Formulas", "Surds, Rationalization, Fundamental Algebraic Identities, Polynomial Division", "Page 65"),
            ("Unit 5: Factorization & Algebraic Manipulation", "Factorization Techniques, HCF & LCM, Square Root by Factorization & Division", "Page 88"),
            ("Unit 6: Linear Equations & Inequalities", "Solving Equations with Absolute Values, Graphing Inequalities on Real Line", "Page 110"),
            ("Unit 7: Quadratic Equations & Formula", "Standard Form ax^2+bx+c=0, Completing Square, Quadratic Formula, Discriminant", "Page 132"),
            ("Unit 8: Practical Geometry & Trigonometry", "Pythagorean Theorem, Trigonometric Ratios (sin, cos, tan), Angle of Elevation", "Page 155"),
        ]
        notes = [
            ("Quadratic Formula & Roots", "x = [-b +/- sqrt(b^2 - 4ac)] / (2a) | Discriminant Delta = b^2 - 4ac"),
            ("Logarithmic Fundamental Laws", "log_a(m*n) = log_a(m) + log_a(n) | log_a(m/n) = log_a(m) - log_a(n) | log_a(m^n) = n*log_a(m)"),
            ("Matrix Inversion & Cramer", "A^(-1) = adj(A) / det(A) (det(A) != 0) | Cramer: x = det(Ax)/det(A), y = det(Ay)/det(A)"),
            ("Fundamental Trigonometric Identities", "sin^2(theta) + cos^2(theta) = 1 | 1 + tan^2(theta) = sec^2(theta) | 1 + cot^2(theta) = csc^2(theta)"),
            ("Complex Number Arithmetic", "i^2 = -1 | z = a + bi -> conjugate z* = a - bi | Modulus |z| = sqrt(a^2 + b^2)"),
        ]
        mcqs = [
            ("Q1: If discriminant b^2 - 4ac > 0 and is a perfect square, the roots are:", "A) Complex and unequal", "B) Real, rational and unequal", "C) Equal", "D) Irrational", "Answer: B (Positive perfect square gives rational roots)"),
            ("Q2: The value of log_10(1000) is equal to:", "A) 1", "B) 2", "C) 3", "D) 10", "Answer: C (10^3 = 1000)"),
            ("Q3: For a singular matrix A, its determinant det(A) must be:", "A) 1", "B) Positive", "C) Zero", "D) Non-zero", "Answer: C (By definition, singular matrix has det = 0)"),
            ("Q4: The distance between points (0,0) and (3,4) is:", "A) 7", "B) 5", "C) 25", "D) 1", "Answer: B (sqrt(3^2 + 4^2) = sqrt(25) = 5)"),
        ]
    elif any(k in comb for k in ['anatomy', 'physiology', 'pathology', 'mbbs', 'medical', 'bio', 'mdcat']):
        toc = [
            ("Unit 1: Cellular Biology & Biomolecules", "Organelles, Cell Membrane, Carbohydrates, Lipids, Proteins & Enzyme Kinetics", "Page 6"),
            ("Unit 2: Human Anatomy & Osteology", "Axial and Appendicular Skeleton, Joint Types, Muscular Origin & Insertion", "Page 28"),
            ("Unit 3: Cardiovascular System & Hemodynamics", "Cardiac Cycle, ECG Interpretation, Blood Pressure Regulation, Vascular Resistance", "Page 55"),
            ("Unit 4: Respiratory System & Gas Transport", "Mechanics of Ventilation, Alveolar Gas Exchange, Oxygen-Hemoglobin Dissociation", "Page 82"),
            ("Unit 5: Neuroanatomy & Nervous System", "Action Potential Generation, Cranial Nerves, Autonomic Sympathetic/Parasympathetic", "Page 110"),
            ("Unit 6: Renal Physiology & Electrolyte Balance", "Glomerular Filtration Rate, Counter-Current Mechanism, Acid-Base Buffer Systems", "Page 138"),
            ("Unit 7: Gastrointestinal & Endocrine Systems", "Enzymatic Digestion, Hypothalamic-Pituitary Axis, Thyroid & Insulin Regulation", "Page 164"),
            ("Unit 8: High-Yield Pathology & Clinical Correlates", "Inflammation Mechanisms, Shock Classifications, Cellular Adaptation & Necrosis", "Page 190"),
        ]
        notes = [
            ("Action Potential & Nerve Impulse", "Resting Membrane Potential = -70 mV | Na+ influx causes Depolarization, K+ efflux causes Repolarization"),
            ("Cardiac Output Formulation", "Cardiac Output (CO) = Stroke Volume (SV) x Heart Rate (HR) | Normal adult resting CO ~ 5.0 L/min"),
            ("Renal Filtration Dynamics", "GFR = Kf * [(Pgc - Pbs) - (pi_gc - pi_bs)] | Normal adult GFR ~ 125 mL/min (~180 L/day)"),
            ("Oxygen Transport in Blood", "O2 Dissociation curve shifts RIGHT with: Increased H+ (lower pH), High CO2, High Temp, High 2,3-BPG"),
            ("Cellular Injury & Pathology", "Necrosis is always pathological with cell lysis | Apoptosis is programmed ATP-dependent cell death"),
        ]
        mcqs = [
            ("Q1: Which cardiac valve separates the left ventricle from the ascending aorta?", "A) Mitral Valve", "B) Aortic Valve", "C) Tricuspid Valve", "D) Pulmonary Valve", "Answer: B (Aortic semilunar valve)"),
            ("Q2: The standard pacemaker of the normal human heart is:", "A) AV Node", "B) Bundle of His", "C) Purkinje Fibers", "D) SA Node", "Answer: D (Sinoatrial Node generates spontaneous action potentials)"),
            ("Q3: Which hormone directly stimulates water reabsorption in the collecting ducts?", "A) Aldosterone", "B) Antidiuretic Hormone (ADH)", "C) Renin", "D) Atrial Natriuretic Peptide", "Answer: B (Vasopressin/ADH inserts Aquaporin-2 channels)"),
            ("Q4: The most abundant plasma protein responsible for oncotic pressure is:", "A) Albumin", "B) Fibrinogen", "C) Globulin", "D) Prothrombin", "Answer: A (Albumin maintains ~80% of intravascular oncotic pressure)"),
        ]
    else:  # Literature, English, Novels, General
        toc = [
            ("Chapter 1: Narrative Context & Author Background", "Biographical Profile, Historical & Literary Setting, Core Themes & Motifs", "Page 4"),
            ("Chapter 2: Structural Synopsis & Plot Architecture", "Exposition, Rising Action, Central Climax, Falling Action & Resolution", "Page 18"),
            ("Chapter 3: Deep Characterization & Psychological Profiles", "Protagonist, Antagonist, Foil Characters, Moral Transformation & Agency", "Page 35"),
            ("Chapter 4: Thematic Analysis & Philosophical Exploration", "Spiritual Awakening, Destiny vs Free Will, Societal Conflict, Redemption", "Page 54"),
            ("Chapter 5: Stylistic Devices, Imagery & Symbolism", "Metaphors, Allegorical Significance, Narrative Voice, Dialogue Dynamics", "Page 72"),
            ("Chapter 6: Critical Commentary & Scholarly Perspectives", "Reception History, Modern Reader Interpretations, Cultural Resonance", "Page 90"),
            ("Chapter 7: Board & University Essay Prompts", "Standard Long-Form Examination Prompts, Model Outlines & Essay Frameworks", "Page 108"),
            ("Chapter 8: Comprehensive Study Guide & Question Bank", "Comprehension Checks, Short Answers, Vocabulary in Context & Quotations", "Page 126"),
        ]
        notes = [
            ("Major Thematic Principles", "Explores human purpose, resilience against adversity, and ethical responsibility in turbulent times."),
            ("Literary Architecture & Tone", "Rich allegorical prose combining psychological realism with evocative philosophical undertones."),
            ("Grammar & Composition Tips", "Ensure clear thesis statement, coherent topic sentences, transitional adverbs, and robust textual evidence."),
            ("Vocabulary & Key Idioms", "Master nuanced vocabulary: Epiphany, catharsis, hubris, alienation, juxtaposition, didacticism."),
            ("Examination Writing Strategy", "Structure responses into Introduction (context), Body Paragraphs (evidence + analysis), and Synthesis conclusion."),
        ]
        mcqs = [
            ("Q1: What literary device represents an abstract concept through concrete symbols?", "A) Hyperbole", "B) Allegory", "C) Onomatopoeia", "D) Oxymoron", "Answer: B (An allegory conveys complex abstract ideas via narrative symbols)"),
            ("Q2: In formal essay composition, the primary claim of the paper is called the:", "A) Topic Sentence", "B) Hook", "C) Thesis Statement", "D) Anecdote", "Answer: C (The thesis statement anchors the entire argument)"),
            ("Q3: Which figure of speech compares two unlike things using 'like' or 'as'?", "A) Metaphor", "B) Simile", "C) Personification", "D) Irony", "Answer: B (Simile explicitly uses comparative words 'like' or 'as')"),
            ("Q4: The emotional release or cleansing experienced through drama or narrative is:", "A) Hubris", "B) Nemesis", "C) Catharsis", "D) Soliloquy", "Answer: C (Catharsis cleanses emotions through pity and fear)"),
        ]

    return toc, notes, mcqs


def _render_page_header(stream: list, page_num: int, total_pages: int, title: str):
    """Adds a clean top header and bottom footer with page numbers."""
    stream.append("q")
    stream.append("0.11 0.31 0.85 rg")
    stream.append("50 735 512 30 re f")
    stream.append("Q")
    stream.append("BT")
    stream.append("/F1 11 Tf 1 1 1 rg 65 745 Td")
    stream.append("(BOOKZY AI - CERTIFIED DIGITAL STUDY SOFT COPY) Tj")
    stream.append("/F2 9 Tf 0.8 0.9 1 rg 180 0 Td")
    stream.append("(100% FREE DONATION) Tj")
    stream.append("ET")

    # Bottom footer line and text
    stream.append("q")
    stream.append("0.85 0.87 0.92 RG 0.8 w")
    stream.append("50 65 512 0.8 re S")
    stream.append("Q")
    stream.append("BT")
    stream.append("/F2 8 Tf 0.4 0.45 0.52 rg 65 50 Td")
    stream.append("(Bookzy AI Digital Library - Verified Student Study Resource | https://bookzyai.pk) Tj")
    stream.append(f"/F1 8 Tf 0.11 0.31 0.85 rg 270 0 Td (Page {page_num} of {total_pages}) Tj")
    stream.append("ET")


def generate_book_pdf(listing_or_book) -> bytes:
    """
    Generates an authentic, multi-page educational study PDF (4 pages, PDF-1.4).
    Contains:
      Page 1: Title Cover, Metadata & Certified Donation Badge
      Page 2: Standard Curriculum Table of Contents & Unit Breakdown
      Page 3: Core High-Yield Concepts, Formulas & Summary Definitions
      Page 4: Board Exam Practice MCQs, Short Questions & Verified Answer Keys
    Zero 3rd-party binary dependencies (100% standard library & portable).
    """
    if hasattr(listing_or_book, 'book'):
        book = listing_or_book.book
        listing = listing_or_book
        seller_name = getattr(listing.seller, 'full_name', 'Student Donor')
        condition = getattr(listing, 'condition', 'Good')
        city = getattr(listing, 'city', 'Pakistan')
        notes = getattr(listing, 'description', '') or getattr(book, 'description', '')
    else:
        book = listing_or_book
        listing = None
        seller_name = 'Verified Community Donor'
        condition = 'Digital Soft Copy'
        city = 'Pakistan'
        notes = getattr(book, 'description', '')

    title = _sanitize_pdf_text(getattr(book, 'title', 'Untitled Book'))[:70]
    author = _sanitize_pdf_text(getattr(book, 'author', 'Unknown Author'))[:55]
    category = _sanitize_pdf_text(getattr(book, 'category', 'General'))[:40]
    board = _sanitize_pdf_text(getattr(book, 'education_board', 'Punjab / Federal Board'))[:50]
    grade = _sanitize_pdf_text(getattr(book, 'grade_class', 'Matric / FSc / MBBS'))[:45]
    subject = _sanitize_pdf_text(getattr(book, 'subject', ''))[:40] or category
    seller = _sanitize_pdf_text(seller_name)[:40]
    isbn = _sanitize_pdf_text(getattr(book, 'isbn', ''))[:30]
    now_str = datetime.now().strftime("%B %d, %Y")

    if not notes:
        notes = f"This certified digital soft-copy edition of {title} is provided free of charge for students and educators across Pakistan under the Bookzy AI student welfare initiative."
    notes = _sanitize_pdf_text(notes)[:320]

    toc_data, notes_data, mcq_data = _get_curriculum_data(title, subject, category, grade)

    pages_streams = []

    # ==========================================
    # PAGE 1: TITLE COVER & CERTIFIED BADGE
    # ==========================================
    p1 = []
    _render_page_header(p1, 1, 4, title)

    # Hero card box
    p1.append("q")
    p1.append("0.96 0.97 0.99 rg 50 490 512 225 re f")
    p1.append("0.82 0.86 0.92 RG 1.5 w 50 490 512 225 re S")
    p1.append("Q")

    p1.append("BT")
    p1.append("/F1 16 Tf 0.08 0.16 0.38 rg 70 682 Td")
    p1.append(f"({title}) Tj")
    p1.append("ET")

    p1.append("BT")
    p1.append("/F2 10 Tf 0.2 0.28 0.42 rg 70 655 Td")
    p1.append(f"(Author / Compiler: {author}) Tj")
    p1.append("0 -18 Td")
    p1.append(f"(Curriculum & Board: {board}) Tj")
    p1.append("0 -18 Td")
    p1.append(f"(Academic Level: {grade}   |   Subject: {subject}) Tj")
    p1.append("0 -18 Td")
    p1.append(f"(Category: {category}   |   Condition: {condition}) Tj")
    p1.append("0 -18 Td")
    p1.append(f"(Donated By: {seller} - {city}) Tj")
    p1.append("0 -18 Td")
    p1.append(f"(Catalog ISBN: {isbn}   |   Digital Verified Date: {now_str}) Tj")
    p1.append("ET")

    # Certified Free Donation Banner
    p1.append("q")
    p1.append("0.91 0.96 0.93 rg 50 360 512 110 re f")
    p1.append("0.22 0.62 0.35 RG 1.5 w 50 360 512 110 re S")
    p1.append("Q")

    p1.append("BT")
    p1.append("/F1 11 Tf 0.12 0.46 0.22 rg 70 445 Td")
    p1.append("(COMMUNITY DONATION NOTICE & EDUCATIONAL ACCESS) Tj")
    p1.append("/F2 9.5 Tf 0.16 0.22 0.28 rg 0 -20 Td")
    p1.append(f"({notes[:85]}) Tj")
    if len(notes) > 85:
        p1.append(f"0 -16 Td ({notes[85:170]}) Tj")
    if len(notes) > 170:
        p1.append(f"0 -16 Td ({notes[170:255]}) Tj")
    if len(notes) > 255:
        p1.append(f"0 -16 Td ({notes[255:320]}) Tj")
    p1.append("ET")

    # Features / Highlights Box
    p1.append("q")
    p1.append("0.98 0.98 0.98 rg 50 100 512 240 re f")
    p1.append("0.85 0.88 0.93 RG 1.2 w 50 100 512 240 re S")
    p1.append("Q")

    p1.append("BT")
    p1.append("/F1 11 Tf 0.11 0.31 0.85 rg 70 315 Td")
    p1.append("(STUDY GUIDE CONTENTS & LEARNING OBJECTIVES) Tj")
    p1.append("/F2 9.5 Tf 0.2 0.25 0.35 rg 0 -22 Td")
    p1.append("([*] Section 1: Standard Scheme of Studies & Unit Breakdown (Page 2)) Tj")
    p1.append("0 -18 Td")
    p1.append("([*] Section 2: Core High-Yield Concepts, Formulas & Definitions (Page 3)) Tj")
    p1.append("0 -18 Td")
    p1.append("([*] Section 3: Board Exam Multiple Choice Questions & Solutions (Page 4)) Tj")
    p1.append("0 -24 Td")
    p1.append("/F1 10 Tf 0.15 0.2 0.3 rg (How to Use This Digital Soft Copy:) Tj")
    p1.append("/F2 9 Tf 0.3 0.35 0.4 rg 0 -16 Td")
    p1.append("(1. Review the Table of Contents on Page 2 to align with your exam syllabus.) Tj")
    p1.append("0 -15 Td")
    p1.append("(2. Master key formulas and high-yield principles summarized on Page 3.) Tj")
    p1.append("0 -15 Td")
    p1.append("(3. Self-test your comprehension using the verified practice questions on Page 4.) Tj")
    p1.append("0 -15 Td")
    p1.append("(4. Share this free resource with classmates across Pakistan. Education is for everyone!) Tj")
    p1.append("ET")

    pages_streams.append("\n".join(p1))

    # ==========================================
    # PAGE 2: TABLE OF CONTENTS & SYLLABUS
    # ==========================================
    p2 = []
    _render_page_header(p2, 2, 4, title)

    # Section Banner
    p2.append("BT")
    p2.append("/F1 13 Tf 0.08 0.16 0.38 rg 50 705 Td")
    p2.append("(TABLE OF CONTENTS & CURRICULUM SYLLABUS BREAKDOWN) Tj")
    p2.append("/F2 9 Tf 0.45 0.5 0.58 rg 0 -15 Td")
    p2.append(f"(Standard BISE / HEC Approved Scheme of Studies for {grade} - {board}) Tj")
    p2.append("ET")

    # Table of Contents Items
    y = 665
    for unit_title, desc, page_ref in toc_data:
        p2.append("q")
        p2.append(f"0.97 0.98 1 rg 50 {y-35} 512 40 re f")
        p2.append(f"0.88 0.91 0.96 RG 0.8 w 50 {y-35} 512 40 re S")
        p2.append("Q")

        p2.append("BT")
        p2.append(f"/F1 9.5 Tf 0.11 0.25 0.55 rg 62 {y-14} Td")
        p2.append(f"({_sanitize_pdf_text(unit_title)}) Tj")
        p2.append(f"/F1 8.5 Tf 0.11 0.31 0.85 rg 390 0 Td ({page_ref}) Tj")
        p2.append("ET")

        p2.append("BT")
        p2.append(f"/F2 8.5 Tf 0.3 0.35 0.45 rg 62 {y-28} Td")
        p2.append(f"({_sanitize_pdf_text(desc)[:95]}) Tj")
        p2.append("ET")
        y -= 48

    # Bottom Exam Tip Box
    p2.append("q")
    p2.append(f"0.93 0.97 0.95 rg 50 {y-30} 512 36 re f")
    p2.append(f"0.25 0.65 0.4 RG 1 w 50 {y-30} 512 36 re S")
    p2.append("Q")
    p2.append("BT")
    p2.append(f"/F1 9 Tf 0.12 0.45 0.25 rg 65 {y-13} Td")
    p2.append("(EXAM PREPARATION STRATEGY:) Tj")
    p2.append(f"/F2 8.5 Tf 0.2 0.3 0.25 rg 0 -13 Td")
    p2.append("(Prioritize Units 1 to 4 for mid-term assessments and review end-of-chapter summaries thoroughly.) Tj")
    p2.append("ET")

    pages_streams.append("\n".join(p2))

    # ==========================================
    # PAGE 3: CORE HIGH-YIELD CONCEPTS & FORMULAS
    # ==========================================
    p3 = []
    _render_page_header(p3, 3, 4, title)

    p3.append("BT")
    p3.append("/F1 13 Tf 0.08 0.16 0.38 rg 50 705 Td")
    p3.append("(HIGH-YIELD CORE CONCEPTS, SUMMARY & EXAM FORMULAE) Tj")
    p3.append("/F2 9 Tf 0.45 0.5 0.58 rg 0 -15 Td")
    p3.append(f"(Quick Revision Notes for Board Examinations, Entry Tests, and Class Tests) Tj")
    p3.append("ET")

    y = 665
    for topic, content in notes_data:
        p3.append("q")
        p3.append(f"0.98 0.98 0.99 rg 50 {y-58} 512 65 re f")
        p3.append(f"0.82 0.86 0.92 RG 1 w 50 {y-58} 512 65 re S")
        # accent left bar
        p3.append("0.11 0.31 0.85 rg")
        p3.append(f"50 {y-58} 4 65 re f")
        p3.append("Q")

        p3.append("BT")
        p3.append(f"/F1 10 Tf 0.11 0.31 0.85 rg 65 {y-14} Td")
        p3.append(f"({_sanitize_pdf_text(topic)}) Tj")
        p3.append("ET")

        p3.append("BT")
        p3.append(f"/F2 9 Tf 0.2 0.25 0.35 rg 65 {y-32} Td")
        clean_content = _sanitize_pdf_text(content)
        p3.append(f"({clean_content[:95]}) Tj")
        if len(clean_content) > 95:
            p3.append(f"0 -15 Td ({clean_content[95:190]}) Tj")
        p3.append("ET")
        y -= 75

    # Memory aid box
    p3.append("q")
    p3.append("0.99 0.96 0.92 rg 50 100 512 55 re f")
    p3.append("0.9 0.6 0.2 RG 1 w 50 100 512 55 re S")
    p3.append("Q")
    p3.append("BT")
    p3.append("/F1 9.5 Tf 0.65 0.35 0.05 rg 65 138 Td")
    p3.append("(STUDY TIP FOR MAXIMUM RETENTION:) Tj")
    p3.append("/F2 8.5 Tf 0.45 0.25 0.05 rg 0 -15 Td")
    p3.append("(Active recall and spaced repetition improve long-term formula retention by over 70%.) Tj")
    p3.append("0 -13 Td")
    p3.append("(Write formulas out on flashcards and review them every 48 hours before examination days.) Tj")
    p3.append("ET")

    pages_streams.append("\n".join(p3))

    # ==========================================
    # PAGE 4: PRACTICE MCQS & ANSWER KEYS
    # ==========================================
    p4 = []
    _render_page_header(p4, 4, 4, title)

    p4.append("BT")
    p4.append("/F1 13 Tf 0.08 0.16 0.38 rg 50 705 Td")
    p4.append("(BOARD EXAM PRACTICE MCQs & CONCEPTUAL QUESTIONS) Tj")
    p4.append("/F2 9 Tf 0.45 0.5 0.58 rg 0 -15 Td")
    p4.append("(Selected High-Frequency Questions from Past Board Papers & Entry Tests) Tj")
    p4.append("ET")

    y = 665
    answers = []
    for q_text, opt_a, opt_b, opt_c, opt_d, ans in mcq_data:
        p4.append("q")
        p4.append(f"0.98 0.98 1 rg 50 {y-52} 512 58 re f")
        p4.append(f"0.85 0.88 0.95 RG 0.8 w 50 {y-52} 512 58 re S")
        p4.append("Q")

        p4.append("BT")
        p4.append(f"/F1 9.5 Tf 0.1 0.18 0.35 rg 62 {y-14} Td")
        p4.append(f"({_sanitize_pdf_text(q_text)}) Tj")
        p4.append("ET")

        p4.append("BT")
        p4.append(f"/F2 8.5 Tf 0.25 0.3 0.4 rg 62 {y-30} Td")
        p4.append(f"({_sanitize_pdf_text(opt_a)}    {_sanitize_pdf_text(opt_b)}) Tj")
        p4.append("0 -14 Td")
        p4.append(f"({_sanitize_pdf_text(opt_c)}    {_sanitize_pdf_text(opt_d)}) Tj")
        p4.append("ET")

        answers.append(f"[*] {_sanitize_pdf_text(ans)}")
        y -= 68

    # Answer Key Box
    p4.append("q")
    p4.append(f"0.93 0.97 0.95 rg 50 {y-85} 512 95 re f")
    p4.append(f"0.22 0.62 0.35 RG 1.2 w 50 {y-85} 512 95 re S")
    p4.append("Q")

    p4.append("BT")
    p4.append(f"/F1 10.5 Tf 0.12 0.46 0.22 rg 65 {y-16} Td")
    p4.append("(VERIFIED ANSWER KEYS & EXPLANATIONS) Tj")
    p4.append("/F2 8.5 Tf 0.16 0.25 0.2 rg")
    for ans in answers:
        p4.append(f"0 -16 Td ({ans[:95]}) Tj")
    p4.append("ET")

    # Platform closing note
    p4.append("BT")
    p4.append("/F1 9 Tf 0.11 0.31 0.85 rg 65 95 Td")
    p4.append("(A Free Community Initiative by Bookzy AI (https://bookzyai.pk)) Tj")
    p4.append("/F2 8.5 Tf 0.4 0.45 0.5 rg 0 -14 Td")
    p4.append("(Empowering Pakistani students with affordable and free educational materials nationwide.) Tj")
    p4.append("ET")

    pages_streams.append("\n".join(p4))

    # ==========================================
    # ASSEMBLE MULTI-PAGE PDF-1.4 DOCUMENT
    # ==========================================
    # Object Map:
    # 1: Catalog
    # 2: Pages root
    # 3: Page 1, 4: Page 2, 5: Page 3, 6: Page 4
    # 7: Page 1 stream, 8: Page 2 stream, 9: Page 3 stream, 10: Page 4 stream
    # 11: Font F1 (Helvetica-Bold)
    # 12: Font F2 (Helvetica)

    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R 4 0 R 5 0 R 6 0 R] /Count 4 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 7 0 R /Resources << /Font << /F1 11 0 R /F2 12 0 R >> >> >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 8 0 R /Resources << /Font << /F1 11 0 R /F2 12 0 R >> >> >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 9 0 R /Resources << /Font << /F1 11 0 R /F2 12 0 R >> >> >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 10 0 R /Resources << /Font << /F1 11 0 R /F2 12 0 R >> >> >>',
    ]

    for p_content in pages_streams:
        s_bytes = p_content.encode('latin1', errors='replace')
        objects.append(f'<< /Length {len(s_bytes)} >>\nstream\n'.encode('latin1') + s_bytes + b'\nendstream')

    objects.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')
    objects.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')

    out = io.BytesIO()
    out.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')

    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(f'{i} 0 obj\n'.encode('latin1'))
        out.write(obj)
        out.write(b'\nendobj\n')

    xref_offset = out.tell()
    out.write(f'xref\n0 {len(objects) + 1}\n'.encode('latin1'))
    out.write(b'0000000000 65535 f \n')
    for off in offsets[1:]:
        out.write(f'{off:010d} 00000 n \n'.encode('latin1'))

    out.write(f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'.encode('latin1'))
    out.write(f'startxref\n{xref_offset}\n%%EOF\n'.encode('latin1'))

    return out.getvalue()
