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

        data = request.get_json() or {}

        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        ime = data.get('ime', '').strip()
        prezime = data.get('prezime', '').strip()
        grad = data.get('grad', '').strip()
        search_term = data.get('q', '').strip()

        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 10))

        base_query = """
            SELECT
                nk.ID,
                c.Email,
                nk.KORISNICKO_IME,
                lpk.IME,
                lpk.PREZIME,
                adr.GRAD,
                nk.PROFILE_PICTURE_URL,
                nk.BLOKIRAN
            FROM Nalog_korisnika nk
            INNER JOIN Licni_podaci_korisnika lpk ON nk.ID = lpk.ID
            LEFT JOIN Adresa_korisnika adr ON nk.ID = adr.ID
            LEFT JOIN Contact_korisnika c ON nk.ID = c.ID
            WHERE nk.ID != :current_user_id
              AND nk.TIP_KORISNIKA = 'user'
        """

        where_conditions = []
        query_params = {'current_user_id': current_user_id}

        if search_term:
            where_conditions.append("""(
                c.EMAIL LIKE :search_term OR
                nk.KORISNICKO_IME LIKE :search_term OR
                lpk.IME LIKE :search_term OR
                lpk.PREZIME LIKE :search_term OR
                adr.GRAD LIKE :search_term
            )""")
            query_params['search_term'] = f'%{search_term}%'
        else:
            if email:
                where_conditions.append("c.EMAIL LIKE :email")
                query_params['email'] = f'%{email}%'

            if username:
                where_conditions.append("nk.KORISNICKO_IME LIKE :korisnicko_ime")
                query_params['korisnicko_ime'] = f'%{username}%'

            if ime:
                where_conditions.append("lpk.IME LIKE :ime")
                query_params['ime'] = f'%{ime}%'

            if prezime:
                where_conditions.append("lpk.PREZIME LIKE :prezime")
                query_params['prezime'] = f'%{prezime}%'

            if grad:
                where_conditions.append("adr.GRAD LIKE :grad")
                query_params['grad'] = f'%{grad}%'

        if where_conditions:
            base_query += " AND " + " AND ".join(where_conditions)

        sort_by = data.get('sort_by', 'KORISNICKO_IME').upper()
        sort_order = data.get('sort_order', 'ASC').upper()

        valid_sort_fields = ['KORISNICKO_IME', 'EMAIL', 'IME', 'PREZIME', 'GRAD']
        if sort_by not in valid_sort_fields:
            sort_by = 'KORISNICKO_IME'
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'ASC'

        if sort_by in ['KORISNICKO_IME', 'EMAIL']:
            base_query += f" ORDER BY nk.{sort_by} {sort_order}"
        elif sort_by in ['IME', 'PREZIME']:
            base_query += f" ORDER BY lpk.{sort_by} {sort_order}"
        else:  # GRAD
            base_query += f" ORDER BY adr.{sort_by} {sort_order}"

        offset = (page - 1) * per_page
        base_query += f" OFFSET {offset} ROWS FETCH NEXT {per_page} ROWS ONLY"

        results = db_client.execute_query(base_query, query_params)

        users = []
        for row in results:
            user_dict = {
                'id': row[0],
                'email': row[1],
                'korisnicko_ime': row[2],
                'ime': row[3],
                'prezime': row[4],
                'grad': row[5],
                'profile_picture_url': row[6],
                'blokiran': row[7]
            }
            users.append(user_dict)

        count_query = """
            SELECT COUNT(*)
            FROM Nalog_korisnika nk
            INNER JOIN Licni_podaci_korisnika lpk ON nk.ID = lpk.ID
            LEFT JOIN Adresa_korisnika adr ON nk.ID = adr.ID
            LEFT JOIN Contact_korisnika c ON nk.ID = c.ID
            WHERE nk.ID != :current_user_id
              AND nk.TIP_KORISNIKA = 'user'
        """
        if where_conditions:
            count_query += " AND " + " AND ".join(where_conditions)

        total_count = db_client.execute_query(count_query, query_params)[0][0]
        total_pages = (total_count + per_page - 1) // per_page

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
                "korisnicko_ime": username,
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