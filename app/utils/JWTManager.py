import jwt
from flask_jwt_extended import get_jwt, jwt_required
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
    
    def checkIfAdmin(self, db_client):
        """
        Check if the user making the request is an admin.
        """
        
        try:
            # Extract the JWT payload
            token_payload = get_jwt()
            

            # Get the user ID (identity) from the token payload
            user_id = token_payload.get("sub")  # `sub` is the standard claim for `identity`
            

            if not user_id:
                raise PermissionError("Invalid token payload: missing user ID")
            # Query to check if the user is an admin
            query = "SELECT Tip_korisnika FROM Nalog_korisnika WHERE ID = :user_id"
            result = db_client.execute_query(query, {"user_id": user_id})
            
            # Validate if the user exists and is an admin
            if not result or result[0][0] != "admin":
                raise PermissionError("User is not authorized to perform this action (Admin vileges required).")
            
        except Exception as e:
            raise PermissionError(f"Failed admin check: {str(e)}")

   
