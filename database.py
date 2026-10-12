"""
database.py - SQLite Database Management for Study Analyzer.

Provides normalized database initialization, connection management,
CRUD operations, and backup/restore capabilities.
"""

import os
import sqlite3
import shutil
from datetime import datetime, date
from typing import List, Dict, Any, Optional

DEFAULT_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "study_analyzer.db")


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Return the database path, ensuring the parent directory exists."""
    path = custom_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a SQLite connection with foreign keys and Row factory enabled."""
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables, indexes, settings, and seed initial curriculum."""
    conn = get_connection(db_path)
    try:
        with conn:
            # 1. Subjects Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT,
                    exam_date TEXT,
                    target_hours REAL DEFAULT 40.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Topics Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    unit_name TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    status TEXT DEFAULT 'Not Started',
                    confidence INTEGER DEFAULT 3,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                );
            """)

            # 3. Tasks Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subject_id INTEGER,
                    planned_minutes INTEGER DEFAULT 60,
                    priority TEXT DEFAULT 'Medium',
                    completed INTEGER DEFAULT 0,
                    completed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
                );
            """)

            # 4. Study Logs Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_date TEXT NOT NULL,
                    subject_id INTEGER,
                    topic TEXT,
                    minutes INTEGER NOT NULL,
                    understanding INTEGER DEFAULT 3,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
                );
            """)

            # 5. Test Results Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_date TEXT NOT NULL,
                    subject_id INTEGER NOT NULL,
                    test_name TEXT NOT NULL,
                    score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                );
            """)

            # 6. Coding Practice Logs Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coding_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    practice_date TEXT NOT NULL,
                    problem_name TEXT NOT NULL,
                    concept TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    attempted INTEGER DEFAULT 1,
                    solved INTEGER DEFAULT 0,
                    independent INTEGER DEFAULT 0,
                    hints_used INTEGER DEFAULT 0,
                    minutes INTEGER DEFAULT 30,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 7. Application Settings Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)

            # Useful indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(task_date);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_study_logs_date ON study_logs(study_date);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_coding_logs_date ON coding_logs(practice_date);")

            # Default settings
            conn.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('daily_academic_target_hours', '3.0');")
            conn.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('daily_coding_target_hours', '1.0');")

            # Seed subjects if empty
            cursor = conn.execute("SELECT COUNT(*) FROM subjects;")
            count = cursor.fetchone()[0]
            if count == 0:
                seed_initial_curriculum(conn)
    finally:
        conn.close()


def seed_initial_curriculum(conn: sqlite3.Connection) -> None:
    """Pre-populate the 5 confirmed semester subjects and syllabus modules."""
    subjects_seed = [
        {
            "code": "BCS701",
            "name": "Internet of Things",
            "exam_date": "2026-11-24",
            "target_hours": 40.0,
            "units": [
                {
                    "unit": "Module 1: IoT Overview & Architecture",
                    "topics": [
                        "What is IoT & Evolution of Connected Devices",
                        "Convergence of IT and OT Networks",
                        "IoT Challenges: Scale, Security, and Interoperability",
                        "IoT Simplified Architecture and Core Building Blocks",
                        "Core IoT Functional Stack and Smart Sensor Layers"
                    ]
                },
                {
                    "unit": "Module 2: Smart Objects & Sensor Networks",
                    "topics": [
                        "Sensors, Actuators, and Smart Objects Overview",
                        "Sensor Characteristics and Classification",
                        "Wireless Sensor Networks (WSN) Architecture",
                        "Connecting Smart Objects: Communications Criteria",
                        "Range, Frequency Bands, and Power Consumption Considerations"
                    ]
                },
                {
                    "unit": "Module 3: IoT Network Layer & Access Technologies",
                    "topics": [
                        "IP as the IoT Network Layer: Architectural Justification",
                        "6LoWPAN: Adaptation Layer, Header Compression, Fragmentation",
                        "6TiSCH and Time Slotted Channel Hopping",
                        "IEEE 802.15.4 Physical and MAC Layer",
                        "Routing Protocol for Low-Power and Lossy Networks (RPL)"
                    ]
                },
                {
                    "unit": "Module 4: Application Protocols & IoT Data Analytics",
                    "topics": [
                        "Constrained Application Protocol (CoAP): Features and Message Types",
                        "Message Queuing Telemetry Transport (MQTT): Publish-Subscribe Model",
                        "Protocol Comparison: CoAP vs MQTT vs HTTP",
                        "Introduction to Data Analytics for IoT and Big Data Pipelines",
                        "Apache Hadoop and MapReduce for Batch IoT Analytics"
                    ]
                },
                {
                    "unit": "Module 5: Industrial IoT & IoT Security",
                    "topics": [
                        "Industrial IoT (IIoT) and Smart Manufacturing Use Cases",
                        "Smart Cities and Connected Vehicle Architectures",
                        "IoT Security Vulnerabilities: Physical, Network, and Cloud",
                        "Securing IoT: Authentication, Encryption, and Access Control",
                        "Privacy Regulations and Trust in IoT Ecosystems"
                    ]
                }
            ]
        },
        {
            "code": "BCS702",
            "name": "Parallel Computing",
            "exam_date": "2026-11-26",
            "target_hours": 40.0,
            "units": [
                {
                    "unit": "Module 1: Foundations of Parallel Computing",
                    "topics": [
                        "Motivations for Parallelism and Moore's Law Limits",
                        "Flynn's Taxonomy: SISD, SIMD, MISD, MIMD",
                        "Shared-Memory vs Distributed-Memory Architectures",
                        "Interconnection Networks: Topologies, Latency, Bandwidth",
                        "Performance Metrics: Speedup, Amdahl's Law, Gustafson's Law"
                    ]
                },
                {
                    "unit": "Module 2: Parallel Algorithm Design & Decomposition",
                    "topics": [
                        "Principles of Parallel Algorithm Design",
                        "Decomposition Techniques: Recursive, Data, Exploratory, Speculative",
                        "Task Graphs, Dependency Trees, and Concurrency",
                        "Mapping Techniques for Load Balancing",
                        "Minimizing Interaction Overheads and Communication Cost"
                    ]
                },
                {
                    "unit": "Module 3: Message Passing Interface (MPI)",
                    "topics": [
                        "Message Passing Model Principles and Communicators",
                        "Basic MPI Routines: MPI_Init, MPI_Comm_rank, MPI_Comm_size",
                        "Point-to-Point Communication: Blocking vs Non-Blocking",
                        "Collective Operations: Broadcast, Scatter, Gather, Reduce",
                        "Derived Datatypes and Topologies in MPI"
                    ]
                },
                {
                    "unit": "Module 4: Shared Memory Programming with OpenMP",
                    "topics": [
                        "OpenMP Execution Model: Fork-Join Paradigm",
                        "Compiler Directives and Parallel Regions",
                        "Work-Sharing Constructs: Parallel For, Sections, Single",
                        "Data Scoping Clauses: Private, Shared, Reduction, Firstprivate",
                        "Synchronization in OpenMP: Critical, Atomic, Barrier, Master"
                    ]
                },
                {
                    "unit": "Module 5: GPU Programming with CUDA",
                    "topics": [
                        "Heterogeneous Computing and GPU Architecture Overview",
                        "CUDA Programming Model: Kernels, Threads, Blocks, Grids",
                        "CUDA Memory Hierarchy: Global, Shared, Constant, Registers",
                        "Thread Synchronization and Warp Divergence",
                        "Case Studies: Matrix Multiplication and Vector Addition in CUDA"
                    ]
                }
            ]
        },
        {
            "code": "BCS703",
            "name": "Cryptography & Network Security",
            "exam_date": "2026-11-30",
            "target_hours": 40.0,
            "units": [
                {
                    "unit": "Module 1: Classical Ciphers & Symmetric Principles",
                    "topics": [
                        "Security Goals (CIA Triad), Attacks, and Mechanisms",
                        "Symmetric Cipher Model and Cryptanalysis Basics",
                        "Substitution Ciphers: Caesar, Monoalphabetic, Playfair, Hill Cipher",
                        "Transposition Ciphers and Rotor Machines",
                        "Stream Ciphers and Pseudorandom Number Generators (LCG, BBS)"
                    ]
                },
                {
                    "unit": "Module 2: Block Ciphers, DES & AES",
                    "topics": [
                        "Feistel Cipher Structure and Principles",
                        "Data Encryption Standard (DES): Key Generation and Round Structure",
                        "Strength of DES, Double DES, Triple DES (3DES)",
                        "Advanced Encryption Standard (AES): S-Box, ShiftRows, MixColumns",
                        "Block Cipher Modes of Operation: ECB, CBC, CFB, OFB, CTR"
                    ]
                },
                {
                    "unit": "Module 3: Public Key Cryptography & Key Exchange",
                    "topics": [
                        "Principles of Asymmetric Key Cryptography and One-Way Functions",
                        "Number Theory Basics: Fermat's & Euler's Theorems, Modulo Arithmetic",
                        "The RSA Algorithm: Key Generation, Encryption, Decryption, Security",
                        "Diffie-Hellman Key Exchange and Man-in-the-Middle Attack",
                        "Introduction to Elliptic Curve Cryptography (ECC)"
                    ]
                },
                {
                    "unit": "Module 4: Hashes, MACs & Digital Signatures",
                    "topics": [
                        "Cryptographic Hash Functions: Properties and Birthday Attack",
                        "Secure Hash Algorithm Family (SHA-256 and SHA-512)",
                        "Message Authentication Codes (MAC) and HMAC Construction",
                        "Digital Signature Schemes: Principles and Requirements",
                        "Digital Signature Standard (DSS) and Public Key Infrastructure (PKI)"
                    ]
                },
                {
                    "unit": "Module 5: Network Security & Protocols",
                    "topics": [
                        "IP Security (IPsec): Architecture, AH, ESP, IKE Protocol",
                        "Transport Layer Security: SSL/TLS Handshake and Record Protocols",
                        "Wireless Network Security: WPA2, WPA3, and Common Attacks",
                        "Firewalls: Packet Filters, Stateful Inspection, Application Gateways",
                        "Intrusion Detection Systems (IDS) and Malicious Software Defense"
                    ]
                }
            ]
        },
        {
            "code": "BCS714D",
            "name": "Big Data Analytics",
            "exam_date": "2026-11-17",
            "target_hours": 40.0,
            "units": [
                {
                    "unit": "Module 1: Introduction to Big Data & Analytics",
                    "topics": [
                        "5 V's of Big Data and Evolution of Big Data Ecosystems",
                        "Traditional Business Intelligence vs Modern Big Data Analytics",
                        "Big Data Analytics Lifecycle and Classification of Analytics",
                        "Architectural Components of Typical Big Data Platforms",
                        "Overview of Analytical Tools and Distributed Frameworks"
                    ]
                },
                {
                    "unit": "Module 2: Hadoop Ecosystem & MapReduce",
                    "topics": [
                        "Hadoop Architecture: NameNode, DataNode, Secondary NameNode",
                        "HDFS Architecture, Block Allocation, Replication, Fault Tolerance",
                        "Hadoop YARN: ResourceManager, NodeManager, ApplicationMaster",
                        "MapReduce Execution: Mapper, Reducer, Combiner, Partitioner",
                        "Sorting, Searching, and Compression in MapReduce Jobs"
                    ]
                },
                {
                    "unit": "Module 3: NoSQL Databases & MongoDB",
                    "topics": [
                        "Limitations of RDBMS and the Need for NoSQL Databases",
                        "NoSQL Categories: Key-Value, Document, Column-Family, Graph",
                        "MongoDB Architecture and Document Data Model",
                        "CRUD Operations and Query Syntax in MongoDB",
                        "Aggregation Pipelines, Indexing, and Replication in MongoDB"
                    ]
                },
                {
                    "unit": "Module 4: Apache Hive & Apache Pig",
                    "topics": [
                        "Apache Hive Architecture, Metastore, and Data Models",
                        "HiveQL: Tables, Partitions, Bucketing, and Joins",
                        "User-Defined Functions (UDFs) in Hive",
                        "Apache Pig Architecture, Pig Latin Operators, and Data Types",
                        "Comparative Study: Pig vs Hive vs Traditional SQL"
                    ]
                },
                {
                    "unit": "Module 5: Apache Spark & Web Analytics",
                    "topics": [
                        "Apache Spark Architecture and In-Memory Computation Paradigm",
                        "Resilient Distributed Datasets (RDDs): Transformations and Actions",
                        "Spark DataFrames and Spark SQL Basics",
                        "Introduction to Text Mining and Web Usage Analytics",
                        "PageRank Algorithm and Web Graph Analysis"
                    ]
                }
            ]
        },
        {
            "code": "BME755D",
            "name": "Non-Conventional Energy Resources",
            "exam_date": "2026-11-19",
            "target_hours": 40.0,
            "units": [
                {
                    "unit": "Module 1: Energy Scenario & Solar Radiation",
                    "topics": [
                        "Global and Indian Energy Reserves, Consumption, and Needs",
                        "Conventional vs Non-Conventional Energy Sources Comparison",
                        "Solar Energy Fundamentals: Extra-terrestrial and Terrestrial Radiation",
                        "Solar Radiation Instruments: Pyranometers and Pyrheliometers",
                        "Solar Radiation Data Analysis and Attenuation in Atmosphere"
                    ]
                },
                {
                    "unit": "Module 2: Solar Geometry & Thermal Collectors",
                    "topics": [
                        "Solar Radiation Geometry: Latitude, Declination, Hour Angle",
                        "Solar Angles: Altitude, Azimuth, Zenith, Local Solar Time",
                        "Solar Concentrators: Cylindrical Parabolic and Paraboloidal Dish",
                        "Working Principle, Applications, and Thermal Gradient of Solar Ponds",
                        "Performance Evaluation of Solar Thermal Concentrators"
                    ]
                },
                {
                    "unit": "Module 3: Flat Plate Collectors & Solar Applications",
                    "topics": [
                        "Liquid Flat Plate Collector Components and Construction",
                        "Basic Energy Balance Equation and Heat Losses",
                        "Transmissivity-Absorptivity (tau-alpha) Product",
                        "Solar Water Heating Systems: Natural Circulation and Forced Circulation",
                        "Solar Photovoltaic (PV) Principles, PV Cell Characteristics, Applications"
                    ]
                },
                {
                    "unit": "Module 4: Wind & Ocean Energy Systems",
                    "topics": [
                        "Wind Energy Fundamentals, Site Selection, Power Density",
                        "Horizontal Axis Wind Turbines (HAWT) vs Vertical Axis (VAWT)",
                        "Wind Turbine Power and Torque Calculations, Betz Limit",
                        "Ocean Thermal Energy Conversion (OTEC): Open and Closed Cycles",
                        "Tidal Energy and Wave Energy Conversion Principles"
                    ]
                },
                {
                    "unit": "Module 5: Biomass, Geothermal & Direct Conversion",
                    "topics": [
                        "Biomass Energy Conversion: Combustion, Gasification, Pyrolysis",
                        "Biogas Plant Designs: Fixed-Dome and Floating-Drum Types",
                        "Factors Affecting Biogas Generation and Methane Production",
                        "Geothermal Energy Systems: Hydrothermal, Geopressured, Hot Dry Rock",
                        "Direct Energy Conversion: Fuel Cells and Magnetohydrodynamic (MHD) Power"
                    ]
                }
            ]
        }
    ]

    for subj in subjects_seed:
        cursor = conn.execute(
            "INSERT INTO subjects (name, code, exam_date, target_hours) VALUES (?, ?, ?, ?);",
            (subj["name"], subj["code"], subj["exam_date"], subj["target_hours"])
        )
        subject_id = cursor.lastrowid
        for u in subj["units"]:
            for t in u["topics"]:
                conn.execute(
                    "INSERT INTO topics (subject_id, unit_name, topic_name, status, confidence) VALUES (?, ?, ?, 'Not Started', 3);",
                    (subject_id, u["unit"], t)
                )


# ==============================================================================
# SUBJECTS CRUD
# ==============================================================================

def get_all_subjects(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all subjects ordered by exam date."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT * FROM subjects ORDER BY exam_date ASC, id ASC;").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_subject_by_id(subject_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return a single subject by ID."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM subjects WHERE id = ?;", (subject_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def add_subject(name: str, code: str, exam_date: str, target_hours: float = 40.0, db_path: Optional[str] = None) -> int:
    """Insert a new subject and return its ID."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO subjects (name, code, exam_date, target_hours) VALUES (?, ?, ?, ?);",
                (name.strip(), code.strip(), exam_date, float(target_hours))
            )
            return cursor.lastrowid
    finally:
        conn.close()


def update_subject(subject_id: int, name: str, code: str, exam_date: str, target_hours: float, db_path: Optional[str] = None) -> bool:
    """Update subject details."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE subjects SET name = ?, code = ?, exam_date = ?, target_hours = ? WHERE id = ?;",
                (name.strip(), code.strip(), exam_date, float(target_hours), subject_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_subject(subject_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a subject and its associated topics (via cascade)."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM subjects WHERE id = ?;", (subject_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# TOPICS CRUD
# ==============================================================================

def get_topics_by_subject(subject_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all topics for a given subject."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM topics WHERE subject_id = ? ORDER BY unit_name ASC, id ASC;",
            (subject_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_topics(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all topics across all subjects with subject name and code."""
    conn = get_connection(db_path)
    try:
        query = """
            SELECT t.*, s.name as subject_name, s.code as subject_code
            FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            ORDER BY s.exam_date ASC, t.unit_name ASC, t.id ASC;
        """
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_topic(subject_id: int, unit_name: str, topic_name: str, status: str = "Not Started", confidence: int = 3, db_path: Optional[str] = None) -> int:
    """Add a new topic."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO topics (subject_id, unit_name, topic_name, status, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
                """,
                (subject_id, unit_name.strip(), topic_name.strip(), status, int(confidence))
            )
            return cursor.lastrowid
    finally:
        conn.close()


def update_topic_status(topic_id: int, status: str, confidence: Optional[int] = None, db_path: Optional[str] = None) -> bool:
    """Update topic completion status and optionally confidence."""
    conn = get_connection(db_path)
    try:
        with conn:
            if confidence is not None:
                cursor = conn.execute(
                    "UPDATE topics SET status = ?, confidence = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                    (status, int(confidence), topic_id)
                )
            else:
                cursor = conn.execute(
                    "UPDATE topics SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                    (status, topic_id)
                )
            return cursor.rowcount > 0
    finally:
        conn.close()


def update_topic(topic_id: int, unit_name: str, topic_name: str, status: str, confidence: int, db_path: Optional[str] = None) -> bool:
    """Update full topic fields."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE topics
                SET unit_name = ?, topic_name = ?, status = ?, confidence = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (unit_name.strip(), topic_name.strip(), status, int(confidence), topic_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_topic(topic_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a topic."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM topics WHERE id = ?;", (topic_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# TASKS CRUD
# ==============================================================================

def get_tasks_by_date(task_date: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return tasks scheduled for a specific date with subject details."""
    conn = get_connection(db_path)
    try:
        query = """
            SELECT t.*, s.name as subject_name, s.code as subject_code
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.task_date = ?
            ORDER BY 
                CASE t.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 ELSE 4 END,
                t.id ASC;
        """
        rows = conn.execute(query, (task_date,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_tasks(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all tasks ordered by date descending."""
    conn = get_connection(db_path)
    try:
        query = """
            SELECT t.*, s.name as subject_name, s.code as subject_code
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            ORDER BY t.task_date DESC, t.id DESC;
        """
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_overdue_tasks(current_date: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return uncompleted tasks dated before current_date without altering original dates."""
    c_date = current_date or date.today().isoformat()
    conn = get_connection(db_path)
    try:
        query = """
            SELECT t.*, s.name as subject_name, s.code as subject_code
            FROM tasks t
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE t.task_date < ? AND t.completed = 0
            ORDER BY t.task_date ASC, 
                CASE t.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;
        """
        rows = conn.execute(query, (c_date,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_task(task_date: str, title: str, category: str, subject_id: Optional[int] = None,
             planned_minutes: int = 60, priority: str = "Medium", db_path: Optional[str] = None) -> int:
    """Add a new task."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (task_date, title, category, subject_id, planned_minutes, priority)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (task_date, title.strip(), category, subject_id, int(planned_minutes), priority)
            )
            return cursor.lastrowid
    finally:
        conn.close()


def update_task(task_id: int, task_date: str, title: str, category: str,
                subject_id: Optional[int], planned_minutes: int, priority: str, db_path: Optional[str] = None) -> bool:
    """Update an existing task."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE tasks
                SET task_date = ?, title = ?, category = ?, subject_id = ?, planned_minutes = ?, priority = ?
                WHERE id = ?;
                """,
                (task_date, title.strip(), category, subject_id, int(planned_minutes), priority, task_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def toggle_task_completion(task_id: int, completed: bool, db_path: Optional[str] = None) -> bool:
    """Toggle completed flag and record completed_at timestamp."""
    conn = get_connection(db_path)
    try:
        with conn:
            now_str = datetime.now().isoformat() if completed else None
            cursor = conn.execute(
                "UPDATE tasks SET completed = ?, completed_at = ? WHERE id = ?;",
                (1 if completed else 0, now_str, task_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_task(task_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a task."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# STUDY LOGS CRUD
# ==============================================================================

def get_study_logs(start_date: Optional[str] = None, end_date: Optional[str] = None,
                   subject_id: Optional[int] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return study session logs with optional filters."""
    conn = get_connection(db_path)
    try:
        query = """
            SELECT l.*, s.name as subject_name, s.code as subject_code
            FROM study_logs l
            LEFT JOIN subjects s ON l.subject_id = s.id
            WHERE 1=1
        """
        params = []
        if start_date:
            query += " AND l.study_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND l.study_date <= ?"
            params.append(end_date)
        if subject_id:
            query += " AND l.subject_id = ?"
            params.append(subject_id)
        query += " ORDER BY l.study_date DESC, l.id DESC;"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_study_log(study_date: str, subject_id: Optional[int], topic: str, minutes: int,
                  understanding: int = 3, notes: str = "", db_path: Optional[str] = None) -> int:
    """Record an actual study session."""
    if minutes <= 0:
        raise ValueError("Study duration must be positive.")
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO study_logs (study_date, subject_id, topic, minutes, understanding, notes)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (study_date, subject_id, topic.strip(), int(minutes), int(understanding), notes.strip())
            )
            return cursor.lastrowid
    finally:
        conn.close()


def update_study_log(log_id: int, study_date: str, subject_id: Optional[int], topic: str,
                     minutes: int, understanding: int, notes: str, db_path: Optional[str] = None) -> bool:
    """Update a study log entry."""
    if minutes <= 0:
        raise ValueError("Study duration must be positive.")
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE study_logs
                SET study_date = ?, subject_id = ?, topic = ?, minutes = ?, understanding = ?, notes = ?
                WHERE id = ?;
                """,
                (study_date, subject_id, topic.strip(), int(minutes), int(understanding), notes.strip(), log_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_study_log(log_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a study log."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM study_logs WHERE id = ?;", (log_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# TEST RESULTS CRUD
# ==============================================================================

def get_test_results(subject_id: Optional[int] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all test results with subject info."""
    conn = get_connection(db_path)
    try:
        query = """
            SELECT r.*, s.name as subject_name, s.code as subject_code
            FROM test_results r
            JOIN subjects s ON r.subject_id = s.id
        """
        params = []
        if subject_id:
            query += " WHERE r.subject_id = ?"
            params.append(subject_id)
        query += " ORDER BY r.test_date DESC, r.id DESC;"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_test_result(test_date: str, subject_id: int, test_name: str, score: float,
                    max_score: float, notes: str = "", db_path: Optional[str] = None) -> int:
    """Insert a test score with validation."""
    if max_score <= 0:
        raise ValueError("Maximum marks must be positive.")
    if score < 0 or score > max_score:
        raise ValueError("Score must be between 0 and maximum marks.")

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO test_results (test_date, subject_id, test_name, score, max_score, notes)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (test_date, subject_id, test_name.strip(), float(score), float(max_score), notes.strip())
            )
            return cursor.lastrowid
    finally:
        conn.close()


def update_test_result(test_id: int, test_date: str, subject_id: int, test_name: str,
                       score: float, max_score: float, notes: str, db_path: Optional[str] = None) -> bool:
    """Update a test result."""
    if max_score <= 0:
        raise ValueError("Maximum marks must be positive.")
    if score < 0 or score > max_score:
        raise ValueError("Score must be between 0 and maximum marks.")

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE test_results
                SET test_date = ?, subject_id = ?, test_name = ?, score = ?, max_score = ?, notes = ?
                WHERE id = ?;
                """,
                (test_date, subject_id, test_name.strip(), float(score), float(max_score), notes.strip(), test_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_test_result(test_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a test result."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM test_results WHERE id = ?;", (test_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# CODING LOGS CRUD
# ==============================================================================

def get_coding_logs(concept: Optional[str] = None, platform: Optional[str] = None,
                    db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return coding practice logs."""
    conn = get_connection(db_path)
    try:
        query = "SELECT * FROM coding_logs WHERE 1=1"
        params = []
        if concept:
            query += " AND concept = ?"
            params.append(concept)
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        query += " ORDER BY practice_date DESC, id DESC;"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_coding_log(practice_date: str, problem_name: str, concept: str, platform: str,
                   attempted: int = 1, solved: int = 0, independent: int = 0,
                   hints_used: int = 0, minutes: int = 30, notes: str = "",
                   db_path: Optional[str] = None) -> int:
    """Add a coding practice entry. Independent requires solved == 1."""
    if minutes < 0:
        raise ValueError("Practice minutes cannot be negative.")
    # A problem cannot be independently solved if it was not solved
    if not solved:
        independent = 0

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO coding_logs (practice_date, problem_name, concept, platform, attempted, solved, independent, hints_used, minutes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (practice_date, problem_name.strip(), concept.strip(), platform.strip(),
                 1 if attempted else 0, 1 if solved else 0, 1 if independent else 0,
                 1 if hints_used else 0, int(minutes), notes.strip())
            )
            return cursor.lastrowid
    finally:
        conn.close()


def update_coding_log(log_id: int, practice_date: str, problem_name: str, concept: str, platform: str,
                      attempted: int, solved: int, independent: int, hints_used: int,
                      minutes: int, notes: str, db_path: Optional[str] = None) -> bool:
    """Update a coding practice entry."""
    if minutes < 0:
        raise ValueError("Practice minutes cannot be negative.")
    if not solved:
        independent = 0

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE coding_logs
                SET practice_date = ?, problem_name = ?, concept = ?, platform = ?,
                    attempted = ?, solved = ?, independent = ?, hints_used = ?, minutes = ?, notes = ?
                WHERE id = ?;
                """,
                (practice_date, problem_name.strip(), concept.strip(), platform.strip(),
                 1 if attempted else 0, 1 if solved else 0, 1 if independent else 0,
                 1 if hints_used else 0, int(minutes), notes.strip(), log_id)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def delete_coding_log(log_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a coding practice entry."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM coding_logs WHERE id = ?;", (log_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================================================================
# SETTINGS & BACKUP/RESTORE
# ==============================================================================

def get_setting(key: str, default_val: str = "", db_path: Optional[str] = None) -> str:
    """Retrieve an app setting value."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?;", (key,)).fetchone()
        return row[0] if row else default_val
    finally:
        conn.close()


def set_setting(key: str, value: str, db_path: Optional[str] = None) -> None:
    """Set or update an app setting value."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?);", (key, str(value)))
    finally:
        conn.close()


def backup_database(destination_path: str, db_path: Optional[str] = None) -> str:
    """Create a clean copy of the SQLite database to destination_path."""
    source = get_db_path(db_path)
    if not os.path.exists(source):
        raise FileNotFoundError(f"Database file not found at {source}")

    os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
    # Using sqlite3 backup API for transactional safety
    source_conn = sqlite3.connect(source)
    dest_conn = sqlite3.connect(destination_path)
    try:
        source_conn.backup(dest_conn)
    finally:
        source_conn.close()
        dest_conn.close()
    return destination_path


def restore_database(source_backup_path: str, db_path: Optional[str] = None) -> bool:
    """Restore the database from a backup file after verifying schema integrity."""
    if not os.path.exists(source_backup_path):
        raise FileNotFoundError(f"Backup file not found at {source_backup_path}")

    # Verify backup is a valid SQLite DB with required tables
    test_conn = sqlite3.connect(source_backup_path)
    try:
        cursor = test_conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        required = ["subjects", "topics", "tasks", "study_logs", "test_results", "coding_logs"]
        for req in required:
            if req not in tables:
                raise ValueError(f"Backup is invalid: missing required table '{req}'")
    finally:
        test_conn.close()

    target = get_db_path(db_path)
    backup_conn = sqlite3.connect(source_backup_path)
    target_conn = sqlite3.connect(target)
    try:
        backup_conn.backup(target_conn)
    finally:
        backup_conn.close()
        target_conn.close()
    return True
