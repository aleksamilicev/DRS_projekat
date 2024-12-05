-- Unos inicijalnih podataka za Licni_podaci_korisnika
INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime)d
VALUES (Licni_podaci_seq.NEXTVAL, 'Marko', 'Markovic');
INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime)
VALUES (Licni_podaci_seq.NEXTVAL, 'Jovana', 'Jovanovic');
INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime)
VALUES (Licni_podaci_seq.NEXTVAL, 'Nikola', 'Nikolic');
INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime)
VALUES (Licni_podaci_seq.NEXTVAL, 'Ana', 'Anic');
INSERT INTO Licni_podaci_korisnika (ID, Ime, Prezime)
VALUES (Licni_podaci_seq.NEXTVAL, 'Milan', 'Milanovic');

SELECT * FROM licni_podaci_korisnika;
--DELETE FROM licni_podaci_korisnika;


-- Unos inicijalnih podataka za Adresa_korisnika
INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava)
VALUES (Adresa_seq.NEXTVAL, 'Bulevar kralja Aleksandra 1', 'Beograd', 'Srbija');
INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava)
VALUES (Adresa_seq.NEXTVAL, 'Ulica Cara Dusana 23', 'Novi Sad', 'Srbija');
INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava)
VALUES (Adresa_seq.NEXTVAL, 'Trg Republike 10', 'Beograd', 'Srbija');
INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava)
VALUES (Adresa_seq.NEXTVAL, 'Bulevar Zorana Djindjica 5', 'Nis', 'Srbija');
INSERT INTO Adresa_korisnika (ID, Ulica, Grad, Drzava)
VALUES (Adresa_seq.NEXTVAL, 'Ulica Kralja Petra 3', 'Kragujevac', 'Srbija');

SELECT      -- Testiranje da li sve radi kako treba
    a.ID AS Adresa_ID,
    a.Ulica,
    a.Grad,
    a.Drzava,
    l.Ime,
    l.Prezime
FROM
    Adresa_korisnika a
JOIN
    Licni_podaci_korisnika l
ON
    a.ID = l.ID;



SELECT * FROM Adresa_korisnika;
--DELETE FROM Adresa_korisnika;

-- Unos inicijalnih podataka za Contact_korisnika
INSERT INTO Contact_korisnika (ID, Broj_telefona, Email)
VALUES (Contact_seq.NEXTVAL, '0641234567', 'marko@example.com');
INSERT INTO Contact_korisnika (ID, Broj_telefona, Email)
VALUES (Contact_seq.NEXTVAL, '0652345678', 'jovana@example.com');
INSERT INTO Contact_korisnika (ID, Broj_telefona, Email)
VALUES (Contact_seq.NEXTVAL, '0633456789', 'nikola@example.com');
INSERT INTO Contact_korisnika (ID, Broj_telefona, Email)
VALUES (Contact_seq.NEXTVAL, '0624567890', 'ana@example.com');
INSERT INTO Contact_korisnika (ID, Broj_telefona, Email)
VALUES (Contact_seq.NEXTVAL, '0615678901', 'milan@example.com');


-- Test upita da bi proverio da li su podaci povezani
SELECT
    L.Ime,
    L.Prezime,
    C.Broj_telefona,
    C.Email
FROM
    Licni_podaci_korisnika L
JOIN
    Contact_korisnika C
    ON L.ID = C.ID;


SELECT * FROM Contact_korisnika;
--DELETE FROM Contact_korisnika;



-- Unos inicijalnih podataka za Nalog_korisnika
INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika, Blokiran)
VALUES (Nalog_seq.NEXTVAL, 'marko123', 'lozinka1', 'admin', 0);
INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika, Blokiran)
VALUES (Nalog_seq.NEXTVAL, 'jovana123', 'lozinka2', 'user', 0);
INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika, Blokiran)
VALUES (Nalog_seq.NEXTVAL, 'nikola123', 'lozinka3', 'user', 1);
INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika, Blokiran)
VALUES (Nalog_seq.NEXTVAL, 'ana123', 'lozinka4', 'user', 0);
INSERT INTO Nalog_korisnika (ID, Korisnicko_ime, Lozinka, Tip_korisnika, Blokiran)
VALUES (Nalog_seq.NEXTVAL, 'milan123', 'lozinka5', 'user', 0);

-- Test da proverimo sve korisnicke naloge
SELECT
    L.Ime,
    L.Prezime,
    N.Korisnicko_ime,
    N.Blokiran
FROM
    Licni_podaci_korisnika L
JOIN
    Nalog_korisnika N
    ON L.ID = N.ID;


SELECT * FROM Nalog_korisnika;
--DELETE FROM Nalog_korisnika;

-- Unos inicijalnih podataka za Osnovni_podaci_objave
INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
VALUES (Objave_seq.NEXTVAL, 1, 0, 'pending');
INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
VALUES (Objave_seq.NEXTVAL, 2, 1, 'approved');
INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
VALUES (Objave_seq.NEXTVAL, 3, 3, 'rejected');
INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
VALUES (Objave_seq.NEXTVAL, 4, 0, 'approved');
INSERT INTO Osnovni_podaci_objave (ID, ID_Korisnika, Broj_odbijanja, Status)
VALUES (Objave_seq.NEXTVAL, 5, 0, 'pending');

-- Test za JOIN izme�u tabela Osnovni_podaci_objave i Licni_podaci_korisnika
SELECT o.ID, o.Status, o.Broj_odbijanja, l.ID AS Korisnik_ID, l.Ime, l.Prezime
FROM Osnovni_podaci_objave o
JOIN Licni_podaci_korisnika l
  ON o.ID_Korisnika = l.ID;

SELECT * FROM Osnovni_podaci_objave;
--DELETE FROM Osnovni_podaci_objave;




-- C:\Users\KORISNIK\Desktop\slike_TEST;
-- Unos podataka u Sadrzaj_objave sa povezivanjem na Osnovni_podaci_objave
INSERT INTO Sadrzaj_objave (ID, Osnovni_podaci_ID, Tekst, Slika)
VALUES (Sadrzaj_objave_seq.NEXTVAL, 1, 'Prva objava', 'C:\Users\KORISNIK\Desktop\slike_TEST\slika1.jpg');
INSERT INTO Sadrzaj_objave (ID, Osnovni_podaci_ID, Tekst, Slika)
VALUES (Sadrzaj_objave_seq.NEXTVAL, 2, 'Druga objava', 'C:\Users\KORISNIK\Desktop\slike_TEST\slika2.jpg');
INSERT INTO Sadrzaj_objave (ID, Osnovni_podaci_ID, Tekst, Slika)
VALUES (Sadrzaj_objave_seq.NEXTVAL, 3, 'Treca objava', 'C:\Users\KORISNIK\Desktop\slike_TEST\slika3.jpg');
INSERT INTO Sadrzaj_objave (ID, Osnovni_podaci_ID, Tekst, Slika)
VALUES (Sadrzaj_objave_seq.NEXTVAL, 4, 'Cetvrta objava', 'C:\Users\KORISNIK\Desktop\slike_TEST\slika4.jpg');
INSERT INTO Sadrzaj_objave (ID, Osnovni_podaci_ID, Tekst, Slika)
VALUES (Sadrzaj_objave_seq.NEXTVAL, 5, 'Peta objava', 'C:\Users\KORISNIK\Desktop\slike_TEST\slika5.jpg');


SELECT 
    opo.ID AS Osnovni_ID,
    opo.ID_Korisnika,
    opo.Status,
    so.ID AS Sadrzaj_ID,
    so.Osnovni_podaci_ID,
    so.Tekst,
    so.Slika
FROM 
    Osnovni_podaci_objave opo
JOIN 
    Sadrzaj_objave so
ON 
    opo.ID = so.Osnovni_podaci_ID;



SELECT * FROM Sadrzaj_objave;
--DELETE FROM Sadrzaj_objave;





-- Unos inicijalnih podataka za Prijateljstva
INSERT INTO Prijateljstva (ID, ID_Korisnika1, ID_Korisnika2, Status)
VALUES (Prijateljstva_seq.NEXTVAL, 1, 2, 'Accepted');
INSERT INTO Prijateljstva (ID, ID_Korisnika1, ID_Korisnika2, Status)
VALUES (Prijateljstva_seq.NEXTVAL, 2, 3, 'Pending');
INSERT INTO Prijateljstva (ID, ID_Korisnika1, ID_Korisnika2, Status)
VALUES (Prijateljstva_seq.NEXTVAL, 3, 4, 'Rejected');
INSERT INTO Prijateljstva (ID, ID_Korisnika1, ID_Korisnika2, Status)
VALUES (Prijateljstva_seq.NEXTVAL, 4, 5, 'Accepted');
INSERT INTO Prijateljstva (ID, ID_Korisnika1, ID_Korisnika2, Status)
VALUES (Prijateljstva_seq.NEXTVAL, 1, 5, 'Pending');

SELECT * FROM Prijateljstva;
--DELETE FROM Prijateljstva;



-- Unos inicijalnih podataka za Osnovni_podaci_notifikacije
INSERT INTO Osnovni_podaci_notifikacije (ID, ID_Korisnika, Status)
VALUES (Notifikacije_seq.NEXTVAL, 1, 'unread');
INSERT INTO Osnovni_podaci_notifikacije (ID, ID_Korisnika, Status)
VALUES (Notifikacije_seq.NEXTVAL, 2, 'read');
INSERT INTO Osnovni_podaci_notifikacije (ID, ID_Korisnika, Status)
VALUES (Notifikacije_seq.NEXTVAL, 3, 'unread');
INSERT INTO Osnovni_podaci_notifikacije (ID, ID_Korisnika, Status)
VALUES (Notifikacije_seq.NEXTVAL, 4, 'read');
INSERT INTO Osnovni_podaci_notifikacije (ID, ID_Korisnika, Status)
VALUES (Notifikacije_seq.NEXTVAL, 5, 'unread');

SELECT * FROM Osnovni_podaci_notifikacije;
--DELETE FROM Osnovni_podaci_notifikacije;





-- Unos inicijalnih podataka za Sadrzaj_notifikacije
INSERT INTO Sadrzaj_notifikacije (ID, Osnovni_podaci_ID, Tekst, Datum_vreme_slanja)
VALUES (Sadrzaj_notifikacije_seq.NEXTVAL, 1, 'Vasa objava je odobrena.', SYSDATE);
INSERT INTO Sadrzaj_notifikacije (ID, Osnovni_podaci_ID, Tekst, Datum_vreme_slanja)
VALUES (Sadrzaj_notifikacije_seq.NEXTVAL, 2, 'Vas zahtev za prijateljstvo je prihvacen.', SYSDATE);
INSERT INTO Sadrzaj_notifikacije (ID, Osnovni_podaci_ID, Tekst, Datum_vreme_slanja)
VALUES (Sadrzaj_notifikacije_seq.NEXTVAL, 3, 'Vas zahtev za prijateljstvo je odbijen.', SYSDATE);
INSERT INTO Sadrzaj_notifikacije (ID, Osnovni_podaci_ID, Tekst, Datum_vreme_slanja)
VALUES (Sadrzaj_notifikacije_seq.NEXTVAL, 4, 'Nova notifikacija!', SYSDATE);
INSERT INTO Sadrzaj_notifikacije (ID, Osnovni_podaci_ID, Tekst, Datum_vreme_slanja)
VALUES (Sadrzaj_notifikacije_seq.NEXTVAL, 5, 'Vasa objava je odobrena.', SYSDATE);



SELECT * FROM Sadrzaj_notifikacije;
--DELETE FROM Sadrzaj_notifikacije;
SELECT * FROM Osnovni_podaci_notifikacije;
--DELETE FROM Osnovni_podaci_notifikacije;
SELECT * FROM Prijateljstva;
--DELETE FROM Prijateljstva;
SELECT * FROM Sadrzaj_objave;
--DELETE FROM Sadrzaj_objave;
SELECT * FROM Osnovni_podaci_objave;
--DELETE FROM Osnovni_podaci_objave;
SELECT * FROM Nalog_korisnika;
--DELETE FROM Nalog_korisnika;
SELECT * FROM Contact_korisnika;
--DELETE FROM Contact_korisnika;
SELECT * FROM Adresa_korisnika;
--DELETE FROM Adresa_korisnika;
SELECT * FROM licni_podaci_korisnika;
--DELETE FROM licni_podaci_korisnika;







