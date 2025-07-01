class Config:
    # Proper connection string with service name
    SQLALCHEMY_DATABASE_URI = (
        #"oracle+cx_oracle://Username:Password@localhost:1521/?service_name=ServiceName)"
        "oracle+cx_oracle://skalarr:sifra123@localhost:1521/?service_name=xepdb1"
    )  
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SQLALCHEMY_ECHO = False  
    