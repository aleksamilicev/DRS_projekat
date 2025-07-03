from flask import jsonify, request, current_app
from sqlalchemy import or_
#from config import db, Nalog_korisnika, Licni_podaci_korisnika, Prijateljstva
import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils import JWTManager

@jwt_required()
def search_users():
    try:
        db_client = current_app.db_client
        current_user_id = get_jwt_identity()
        
        # Preuzimanje parametara za pretragu iz query string-a
        email = request.args.get('email', '').strip()
        username = request.args.get('username', '').strip()
        ime = request.args.get('ime', '').strip()
        prezime = request.args.get('prezime', '').strip()
        grad = request.args.get('grad', '').strip()
        
        # Opšti search term
        search_term = request.args.get('q', '').strip()
        
        # Parametri za paginaciju
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Kreiranje base query-ja
        base_query = """
            SELECT
                nk.ID,
                nk.Email,
                nk.Username,
                lpk.Ime,
                lpk.Prezime,
                lpk.Grad,
                nk.profile_picture_url,
                nk.Blokiran
            FROM Nalog_korisnika nk
            INNER JOIN Licni_podaci_korisnika lpk ON nk.ID = lpk.ID
            WHERE nk.ID != :current_user_id
              AND nk.Tip_korisnika = 'user'
        """
        
        # Lista uslova za WHERE klauzulu
        where_conditions = []
        query_params = {'current_user_id': current_user_id}
        
        # Ako je prosleđen opšti search term, koristi ga za pretragu po svim poljima
        if search_term:
            where_conditions.append("""(
                nk.Email LIKE :search_term OR
                nk.Username LIKE :search_term OR
                lpk.Ime LIKE :search_term OR
                lpk.Prezime LIKE :search_term OR
                lpk.Grad LIKE :search_term
            )""")
            query_params['search_term'] = f'%{search_term}%'
        
        # Inače, koristi specifične parametre
        else:
            # Dodavanje uslova na osnovu prosleđenih parametara
            if email:
                where_conditions.append("nk.Email LIKE :email")
                query_params['email'] = f'%{email}%'
            
            if username:
                where_conditions.append("nk.Username LIKE :username")
                query_params['username'] = f'%{username}%'
            
            if ime:
                where_conditions.append("lpk.Ime LIKE :ime")
                query_params['ime'] = f'%{ime}%'
            
            if prezime:
                where_conditions.append("lpk.Prezime LIKE :prezime")
                query_params['prezime'] = f'%{prezime}%'
            
            if grad:
                where_conditions.append("lpk.Grad LIKE :grad")
                query_params['grad'] = f'%{grad}%'
        
        # Dodavanje WHERE uslova u query
        if where_conditions:
            base_query += " AND " + " AND ".join(where_conditions)
        
        # Dodavanje sortiranja
        sort_by = request.args.get('sort_by', 'Username')
        sort_order = request.args.get('sort_order', 'ASC')
        
        # Validacija sort polja
        valid_sort_fields = ['Username', 'Email', 'Ime', 'Prezime', 'Grad']
        if sort_by not in valid_sort_fields:
            sort_by = 'Username'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'ASC'
        
        # Dodavanje ORDER BY
        if sort_by in ['Username', 'Email']:
            base_query += f" ORDER BY nk.{sort_by} {sort_order}"
        else:
            base_query += f" ORDER BY lpk.{sort_by} {sort_order}"
        
        # Dodavanje LIMIT i OFFSET za paginaciju
        offset = (page - 1) * per_page
        base_query += f" OFFSET {offset} ROWS FETCH NEXT {per_page} ROWS ONLY"
        
        # Izvršavanje query-ja
        results = db_client.execute_query(base_query, query_params)
        
        # Formatiranje rezultata
        users = []
        for row in results:
            user_dict = {
                'id': row[0],
                'email': row[1],
                'username': row[2],
                'ime': row[3],
                'prezime': row[4],
                'grad': row[5],
                'profile_picture_url': row[6],
                'blokiran': row[7]
            }
            users.append(user_dict)
        
        # Query za ukupan broj rezultata (za paginaciju)
        count_query = """
            SELECT COUNT(*)
            FROM Nalog_korisnika nk
            INNER JOIN Licni_podaci_korisnika lpk ON nk.ID = lpk.ID
            WHERE nk.ID != :current_user_id
              AND nk.Tip_korisnika = 'user'
        """
        
        # Dodavanje WHERE uslova i u count query
        if where_conditions:
            count_query += " AND " + " AND ".join(where_conditions)
        
        total_count = db_client.execute_query(count_query, query_params)[0][0]
        total_pages = (total_count + per_page - 1) // per_page
        
        # Vraćanje rezultata
        return jsonify({
            "success": True,
            "message": "Search completed successfully",
            "data": {
                "users": users,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            },
            "search_params": {
                "email": email,
                "username": username,
                "ime": ime,
                "prezime": prezime,
                "grad": grad,
                "search_term": search_term,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to search users", "details": str(e)}), 500