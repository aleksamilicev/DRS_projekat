class EmailText:
    
    def register_pending(user: str):
        return f"""
        Dear {user},
        
        Thank you for registering on DRS Projekat. Your account is currently pending approval from our administrators. 
        
        You will receive a notification once your registration has been reviewed. This process usually takes 24-48 hours. 
        
        If you have any questions, feel free to contact us at drsprojekat7@gmail.com.
        
        Best regards,  
        DRS Projekat Team
        """

    
    def register_approved(user: str):
        return f"""
        Dear {user},
        
        Congratulations! Your account has been approved by our administrators. You can now log in and start using DRS Projekat.
        
        If you need any assistance, feel free to contact our support team at drsprojekat7@gmail.com.
        
        Welcome aboard!
        
        Best regards,  
        DRS Projekat Team
        """

    
    def register_rejected(user: str):
        return f"""
        Dear {user},
        
        We regret to inform you that your registration request for DRS Projekat has been declined by our administrators.
            
        If you believe this was a mistake or would like further clarification, please contact us at drsprojekat7@gmail.com.
        
        Thank you for your interest in DRS Projekat.
        
        Best regards,  
        DRS Projekat Team
        """