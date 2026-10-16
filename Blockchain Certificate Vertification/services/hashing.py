import hashlib

def create_canonical_string(student_id: str, certificate_id: str, course_name: str, issuer: str, completion_date: str) -> str:
    """
    Creates a standardized, deterministic canonical string for certificate verification.
    Format: student_id|certificate_id|course_name|issuer|completion_date
    """
    s_id = str(student_id).strip()
    c_id = str(certificate_id).strip()
    course = str(course_name).strip()
    iss = str(issuer).strip()
    date = str(completion_date).strip()
    
    canonical_str = f"{s_id}|{c_id}|{course}|{iss}|{date}"
    return canonical_str

def generate_certificate_hash(student_id: str, certificate_id: str, course_name: str, issuer: str, completion_date: str) -> str:
    """
    Generates a deterministic SHA-256 hash from canonical certificate data.
    """
    canonical_str = create_canonical_string(student_id, certificate_id, course_name, issuer, completion_date)
    sha256_hash = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
    return sha256_hash
