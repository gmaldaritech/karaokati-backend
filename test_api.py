import requests
import json
from typing import Optional

# Configurazione
BASE_URL = "http://localhost:8000/api/v1"
token: Optional[str] = None
dj_id: Optional[int] = None
venue_id: Optional[int] = None
song_id: Optional[int] = None
booking_id: Optional[int] = None

# Colori per output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_section(title: str):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def make_request(method: str, endpoint: str, data: dict = None, use_auth: bool = False):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if use_auth and token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"DEBUG - Making {method} request to: {url}")  # ← DEBUG
    print(f"DEBUG - Data: {data}")  # ← DEBUG
    print(f"DEBUG - Headers: {headers}")  # ← DEBUG
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"DEBUG - Response received: {response}")  # ← DEBUG
        print(f"DEBUG - Status code: {response.status_code}")  # ← DEBUG
        
        return response
    except Exception as e:
        print_error(f"Errore di connessione: {e}")
        print(f"DEBUG - Exception type: {type(e)}")  # ← DEBUG
        return None

# ==================== TEST AUTHENTICATION ====================

def test_register_success():
    print_section("TEST 1: Registrazione DJ - Successo")
    
    data = {
        "full_name": "Mario Rossi",
        "stage_name": "DJ Mario",
        "email": "mario@karaokati.com",
        "phone": "+39 333 1234567",
        "password": "password123"
    }
    
    response = make_request("POST", "/auth/register", data)
    
    if response.status_code == 201:
        result = response.json()
        global token, dj_id
        token = result.get("token")
        dj_id = result.get("dj", {}).get("id")
        
        print_success(f"Registrazione completata")
        print_info(f"DJ ID: {dj_id}")
        print_info(f"QR Code: {result.get('dj', {}).get('qr_code_id')}")
        print_info(f"Token: {token[:30]}...")
        return True
    else:
        print_error(f"Registrazione fallita: {response.status_code}")
        print_error(f"Dettaglio: {response.json()}")
        return False

def test_register_duplicate_email():
    print_section("TEST 2: Registrazione DJ - Email Duplicata (NEGATIVO)")
    
    data = {
        "full_name": "Luigi Verdi",
        "stage_name": "DJ Luigi",
        "email": "mario@karaokati.com",  # Email già usata
        "password": "password123"
    }
    
    response = make_request("POST", "/auth/register", data)
    
    if response.status_code == 400:
        print_success("Errore correttamente rilevato: Email duplicata")
        print_info(f"Messaggio: {response.json().get('detail')}")
        return True
    else:
        print_error("Il sistema avrebbe dovuto rifiutare la registrazione!")
        return False

def test_login_success():
    print_section("TEST 3: Login - Successo")
    
    data = {
        "email": "mario@karaokati.com",
        "password": "password123"
    }
    
    response = make_request("POST", "/auth/login", data)
    
    if response.status_code == 200:
        result = response.json()
        new_token = result.get("token")
        print_success("Login completato")
        print_info(f"Token ricevuto: {new_token[:30]}...")
        return True
    else:
        print_error(f"Login fallito: {response.status_code}")
        return False

def test_login_wrong_password():
    print_section("TEST 4: Login - Password Errata (NEGATIVO)")
    
    data = {
        "email": "mario@karaokati.com",
        "password": "wrongpassword"
    }
    
    response = make_request("POST", "/auth/login", data)
    
    if response.status_code == 401:
        print_success("Errore correttamente rilevato: Password errata")
        print_info(f"Messaggio: {response.json().get('detail')}")
        return True
    else:
        print_error("Il sistema avrebbe dovuto rifiutare il login!")
        return False

# ==================== TEST VENUES ====================

def test_create_venue_success():
    print_section("TEST 5: Creazione Locale - Successo")
    
    data = {
        "name": "Locale Rock",
        "address": "Via Roma 123, Milano",
        "capacity": 200
    }
    
    response = make_request("POST", "/venues", data, use_auth=True)
    
    if response.status_code == 201:
        result = response.json()
        global venue_id
        venue_id = result.get("id")
        print_success(f"Locale creato: {result.get('name')}")
        print_info(f"Venue ID: {venue_id}")
        return True
    else:
        print_error(f"Creazione fallita: {response.status_code}")
        return False

def test_create_venue_without_auth():
    print_section("TEST 6: Creazione Locale - Senza Autenticazione (NEGATIVO)")
    
    data = {
        "name": "Locale Senza Auth",
        "address": "Via Test 1",
        "capacity": 100
    }
    
    response = make_request("POST", "/venues", data, use_auth=False)
    
    if response.status_code == 403:
        print_success("Errore correttamente rilevato: Autenticazione richiesta")
        return True
    else:
        print_error("Il sistema avrebbe dovuto richiedere autenticazione!")
        return False

def test_list_venues():
    print_section("TEST 7: Lista Locali - Successo")
    
    response = make_request("GET", "/venues", use_auth=True)
    
    if response.status_code == 200:
        venues = response.json()
        print_success(f"Locali trovati: {len(venues)}")
        for venue in venues:
            print_info(f"  - {venue['name']} (ID: {venue['id']}, Active: {venue['active']})")
        return True
    else:
        print_error("Impossibile ottenere lista locali")
        return False

def test_toggle_venue():
    print_section("TEST 8: Attivazione Locale - Successo")
    
    response = make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Locale {'attivato' if result['active'] else 'disattivato'}")
        return True
    else:
        print_error("Impossibile cambiare stato locale")
        return False

# ==================== TEST SONGS ====================

def test_add_song_success():
    print_section("TEST 9: Aggiunta Canzone - Successo")
    
    data = {
        "file_name": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3"
    }
    
    response = make_request("POST", "/songs", data, use_auth=True)
    
    if response.status_code == 201:
        result = response.json()
        global song_id
        song_id = result.get("id")
        print_success(f"Canzone aggiunta: {result.get('file_name')}")
        print_info(f"Song ID: {song_id}")
        return True
    else:
        print_error("Impossibile aggiungere canzone")
        return False

def test_bulk_add_songs():
    print_section("TEST 10: Importazione Massiva Canzoni - Successo")
    
    data = {
        "songs": [
            "Jovanotti - Bella - Radio Edit.mp3",
            "Umberto Tozzi - Gloria - Original Version.mp3",
            "Al Bano & Romina Power - Felicità.mp3",
            "Toto Cutugno - L'Italiano - Live Version.mp3"
        ]
    }
    
    response = make_request("POST", "/songs/bulk", data, use_auth=True)
    
    if response.status_code == 201:
        result = response.json()
        print_success(f"{result['count']} canzoni aggiunte")
        return True
    else:
        print_error("Importazione fallita")
        return False

def test_search_songs():
    print_section("TEST 11: Ricerca Canzoni - Successo")
    
    response = make_request("GET", "/songs", {"search": "bella"}, use_auth=True)
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Trovate {len(result['songs'])} canzoni con 'bella'")
        for song in result['songs']:
            print_info(f"  - {song['file_name']}")
        return True
    else:
        print_error("Ricerca fallita")
        return False

def test_list_songs_pagination():
    print_section("TEST 12: Lista Canzoni con Paginazione - Successo")
    
    response = make_request("GET", "/songs", {"page": 1, "per_page": 3}, use_auth=True)
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Pagina 1: {len(result['songs'])} canzoni")
        print_info(f"Totale canzoni: {result['total']}")
        print_info(f"Pagine totali: {result['pages']}")
        return True
    else:
        print_error("Paginazione fallita")
        return False

# ==================== TEST BOOKINGS ====================

def test_create_booking_success():
    print_section("TEST 13: Creazione Prenotazione - Successo")
    
    data = {
        "user_name": "Marco",
        "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "key": "+2",
        "venue_id": venue_id
    }
    
    response = make_request("POST", "/bookings", data, use_auth=True)
    
    if response.status_code == 201:
        result = response.json()
        global booking_id
        booking_id = result.get("id")
        print_success(f"Prenotazione creata per {result.get('user_name')}")
        print_info(f"Booking ID: {booking_id}")
        print_info(f"Status: {result.get('status')}")
        return True
    else:
        print_error("Creazione prenotazione fallita")
        return False

def test_create_booking_invalid_venue():
    print_section("TEST 14: Creazione Prenotazione - Locale Inesistente (NEGATIVO)")
    
    data = {
        "user_name": "Laura",
        "song": "Test Song.mp3",
        "key": "0",
        "venue_id": 99999  # ID inesistente
    }
    
    response = make_request("POST", "/bookings", data, use_auth=True)
    
    if response.status_code == 404:
        print_success("Errore correttamente rilevato: Locale non trovato")
        return True
    else:
        print_error("Il sistema avrebbe dovuto rifiutare la prenotazione!")
        return False

def test_list_bookings():
    print_section("TEST 15: Lista Prenotazioni - Successo")
    
    response = make_request("GET", "/bookings", {"venue_id": venue_id}, use_auth=True)
    
    if response.status_code == 200:
        bookings = response.json()
        print_success(f"Prenotazioni trovate: {len(bookings)}")
        for booking in bookings:
            print_info(f"  - {booking['user_name']}: {booking['song']} ({booking['status']})")
        return True
    else:
        print_error("Impossibile ottenere prenotazioni")
        return False

def test_accept_booking():
    print_section("TEST 16: Accettazione Prenotazione - Successo")
    
    response = make_request("POST", f"/bookings/{booking_id}/accept", use_auth=True)
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Prenotazione accettata: {result['message']}")
        return True
    else:
        print_error("Impossibile accettare prenotazione")
        return False

def test_delete_booking():
    print_section("TEST 17: Eliminazione Prenotazione - Successo")
    
    response = make_request("DELETE", f"/bookings/{booking_id}", use_auth=True)
    
    if response.status_code == 200:
        print_success("Prenotazione eliminata")
        return True
    else:
        print_error("Impossibile eliminare prenotazione")
        return False

# ==================== TEST CLEANUP ====================

def test_cleanup():
    print_section("TEST 18: Pulizia Dati Test")
    
    # Elimina venue (che cancellerà anche le prenotazioni in cascata)
    if venue_id:
        response = make_request("DELETE", f"/venues/{venue_id}", use_auth=True)
        if response.status_code == 200:
            print_success("Locale eliminato")
        
    # Elimina tutte le canzoni
    response = make_request("DELETE", "/songs", use_auth=True)
    if response.status_code == 200:
        result = response.json()
        print_success(f"Catalogo eliminato: {result['deleted']} canzoni")
    
    return True

# ==================== MAIN ====================

def run_all_tests():
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  🧪 KARAOKATI API TEST SUITE")
    print(f"  Base URL: {BASE_URL}")
    print(f"{'='*60}{Colors.END}\n")
    
    tests = [
        # Authentication
        ("Registrazione Successo", test_register_success),
        #("Registrazione Email Duplicata", test_register_duplicate_email),
        ("Login Successo", test_login_success),
        #("Login Password Errata", test_login_wrong_password),
        
        # Venues
        ("Creazione Locale Successo", test_create_venue_success),
        #("Creazione Locale Senza Auth", test_create_venue_without_auth),
        ("Lista Locali", test_list_venues),
        ("Attivazione Locale", test_toggle_venue),
        
        # Songs
        ("Aggiunta Canzone", test_add_song_success),
        ("Importazione Massiva", test_bulk_add_songs),
        ("Ricerca Canzoni", test_search_songs),
        ("Paginazione Canzoni", test_list_songs_pagination),
        
        # Bookings
        ("Creazione Prenotazione", test_create_booking_success),
        #("Prenotazione Locale Inesistente", test_create_booking_invalid_venue),
        ("Lista Prenotazioni", test_list_bookings),
        ("Accettazione Prenotazione", test_accept_booking),
        #("Eliminazione Prenotazione", test_delete_booking),
        
        # Cleanup
        #("Pulizia Dati", test_cleanup),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Eccezione: {e}")
            failed += 1
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  📊 RISULTATI")
    print(f"{'='*60}{Colors.END}\n")
    
    total = passed + failed
    print(f"Totale test: {total}")
    print(f"{Colors.GREEN}✓ Passati: {passed}{Colors.END}")
    print(f"{Colors.RED}✗ Falliti: {failed}{Colors.END}")
    
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\nSuccesso: {percentage:.1f}%\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}🎉 TUTTI I TEST PASSATI! 🎉{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠ Alcuni test sono falliti{Colors.END}\n")

if __name__ == "__main__":
    run_all_tests()