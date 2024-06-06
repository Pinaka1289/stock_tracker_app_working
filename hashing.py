from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash():
    @staticmethod
    def bcrypt(password: str):
        """
        Hashes the provided password using bcrypt.

        Args:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
        """
        return pwd_cxt.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        """
        Verifies a plain password against a hashed password.

        Args:
            hashed_password (str): The hashed password.
            plain_password (str): The plain password to verify.

        Returns:
            bool: True if the password matches the hashed password, False otherwise.
        """
        return pwd_cxt.verify(plain_password, hashed_password)
