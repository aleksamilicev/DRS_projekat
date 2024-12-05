import jwt

secret_key = "nas_secret_key_koji_bi_trebalo_da_se_nalazi_u_nekom_config_fileu"

class JWTManager:
    def __init__(self, algorithm="HS256"):
        """
        Initializes the JWTManager with a secret key and algorithm.

        :param secret_key: The secret key used for signing and verifying tokens.
        :param algorithm: The algorithm to use for token generation (default: HS256).
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, payload):
        """
        Create a JWT token with the given payload.

        :param payload: Dictionary containing the payload data.
        :return: Signed JWT token as a string.
        """
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token):
        """
        Verify the provided JWT token.

        :param token: The JWT token to verify.
        :return: Decoded payload if token is valid.
        :raises jwt.InvalidTokenError: If the token is invalid.
        """
        try:
            decoded_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded_payload
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")