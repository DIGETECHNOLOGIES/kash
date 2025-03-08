from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.timezone import now
import datetime

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _num_seconds(self, dt):
        """Convert datetime to seconds since epoch."""
        return int(dt.timestamp())

    def make_token(self, user):
        """Generate a token with a timestamp."""
        timestamp = self._num_seconds(now())  # Get current timestamp
        return super().make_token(user) + f"-{timestamp}"

    def check_token(self, user, token):
        """Check if the token is valid and not expired."""
        if not (user and token):
            return False
        
        try:
            token_parts = token.rsplit("-", 1)
            if len(token_parts) != 2:
                return False
            
            base_token, token_time = token_parts
            token_time = int(token_time)  # Convert to integer timestamp
        except ValueError:
            return False

        # Validate token structure
        is_valid = super().check_token(user, base_token)
        if not is_valid:
            return False

        # Check if token is within the 10-minute validity period
        current_time = self._num_seconds(now())
        return (current_time - token_time) <= 600  # 600 seconds = 10 minutes

account_activation_token = AccountActivationTokenGenerator()
