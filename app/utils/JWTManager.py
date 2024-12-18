import jwt

secret_key = "nas_secret_key_koji_bi_trebalo_da_se_nalazi_u_nekom_config_fileu"

class JWTManager:
    def __init__(self, algorithm="HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, payload):
        # Generate a token without expiration (`exp` claim)
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token):
        try:
            decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded_payload
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def extract_and_verify_token(self, headers):
        """
        Extracts the JWT token from the Authorization header, verifies it, 
        and returns the decoded payload.
        """
        auth_header = headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValueError("Authorization token is missing or invalid")

        # Extract the token from the Authorization header
        token = auth_header.split(" ")[1]  # Remove the "Bearer " prefix

        # Verify and decode the token
        return self.verify_token(token)
