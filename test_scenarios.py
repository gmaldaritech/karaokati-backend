#!/usr/bin/env python3
"""
Karaokati API - Complete Booking System Test Suite
Tests booking functionality with session_id integration + Negative Tests

This test suite covers:
- DJ manual bookings (session_id = NULL)
- User session-based bookings (session_id = UUID)
- Session management and validation
- Rate limiting (max 3 bookings per session)
- User isolation (each user sees only their bookings)
- DJ sees all bookings from all users
- Negative test cases for error scenarios

Based on project documentation from TODO.md and DATABASE_SCHEMA.md
"""

import requests
import json
from typing import Optional
import time

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "http://localhost:8000/api/v1"

# Test data storage
token: Optional[str] = None
dj_id: Optional[int] = None
venue_id: Optional[int] = None
qr_code_id: Optional[str] = None
session_1_cookie: Optional[dict] = None
session_2_cookie: Optional[dict] = None
session_4_cookie: Optional[dict] = None
session_1_id: Optional[str] = None
session_2_id: Optional[str] = None
session_4_id: Optional[str] = None

# =============================================================================
# COLORS FOR OUTPUT
# =============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
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
    print(f"\n{Colors.PURPLE}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.END}\n")

def print_subsection(title: str):
    print(f"\n{Colors.CYAN}--- {title} ---{Colors.END}")

# =============================================================================
# HTTP REQUEST HELPER
# =============================================================================

def make_request(method: str, endpoint: str, data: dict = None, 
                 use_auth: bool = False, cookies: dict = None, 
                 allow_redirects: bool = False):
    """Make HTTP request with optional auth and cookies"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if use_auth and token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(
                url, 
                headers=headers, 
                params=data, 
                cookies=cookies,
                allow_redirects=allow_redirects
            )
        elif method == "POST":
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                cookies=cookies,
                allow_redirects=allow_redirects
            )
        elif method == "PUT":
            response = requests.put(
                url, 
                headers=headers, 
                json=data, 
                cookies=cookies
            )
        elif method == "DELETE":
            response = requests.delete(
                url, 
                headers=headers, 
                cookies=cookies
            )
        
        return response
    except Exception as e:
        print_error(f"Errore di connessione: {e}")
        return None

# =============================================================================
# SETUP: Create DJ and Venue
# =============================================================================

def setup_dj_and_venue():
    """Setup iniziale: crea DJ, venue e canzoni"""
    print_section("SETUP: Preparazione Ambiente Test")
    
    global token, dj_id, venue_id, qr_code_id
    
    # 1. Registra DJ
    print_subsection("1. Registrazione DJ")
    data = {
        "full_name": "Test DJ",
        "stage_name": "DJ Test",
        "email": "test_123456@karaokati.com",
        "phone": "+39 333 1234567",
        "password": "password123"
    }
    
    response = make_request("POST", "/auth/register", data)
    
    if response and response.status_code == 201:
        result = response.json()
        token = result.get("token")
        dj_id = result.get("dj", {}).get("id")
        qr_code_id = result.get("dj", {}).get("qr_code_id")
        print_success(f"DJ registrato - ID: {dj_id}, QR: {qr_code_id}")
    else:
        print_error("Registrazione DJ fallita")
        if response:
            print_error(f"Status: {response.status_code}, Response: {response.text}")
        return False
    
    # 2. Crea venue
    print_subsection("2. Creazione Venue")
    data = {"name": "Test Venue", "address": "Via Test 123", "capacity": 100}
    response = make_request("POST", "/venues", data, use_auth=True)
    
    if response and response.status_code == 201:
        result = response.json()
        venue_id = result.get("id")
        print_success(f"Venue creato - ID: {venue_id}")
    else:
        print_error("Creazione venue fallita")
        return False
    
    # 3. Attiva venue
    print_subsection("3. Attivazione Venue")
    response = make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    
    if response and response.status_code == 200:
        print_success("Venue attivato")
    else:
        print_error("Attivazione venue fallita")
        return False
    
    # 4. Aggiungi canzoni
    print_subsection("4. Aggiunta Canzoni")
    songs = [
        "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "Jovanotti - Bella - Radio Edit.mp3",
        "Umberto Tozzi - Gloria - Original Version.mp3",
        "Al Bano & Romina Power - Felicità.mp3",
        "Toto Cutugno - L'Italiano - Live Version.mp3"
    ]
    
    response = make_request("POST", "/songs/bulk", {"songs": songs}, use_auth=True)
    
    if response and response.status_code == 201:
        print_success(f"{len(songs)} canzoni aggiunte")
    else:
        print_error("Aggiunta canzoni fallita")
        return False
    
    print_success("✓ Setup completato con successo!\n")
    return True

# =============================================================================
# TEST 1: DJ Manual Booking (session_id = NULL)
# =============================================================================

def test_dj_manual_booking_null_session():
    """TEST 1: DJ crea prenotazione manuale (session_id deve essere NULL)"""
    print_section("TEST 1: DJ Manual Booking - session_id NULL")
    
    data = {
        "user_name": "Marco (DJ manual)",
        "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "key": "+2",
        "venue_id": venue_id
    }
    
    response = make_request("POST", "/bookings", data, use_auth=True)
    
    if not response or response.status_code != 201:
        print_error("Creazione prenotazione DJ fallita")
        if response:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
        return False
    
    result = response.json()
    
    # ✅ Verifica session_id = NULL
    if result.get("session_id") is None:
        print_success("✓ session_id è NULL (corretto per prenotazione DJ)")
    else:
        print_error(f"✗ session_id dovrebbe essere NULL, trovato: {result.get('session_id')}")
        return False
    
    # ✅ Verifica status = accepted
    if result.get("status") == "accepted":
        print_success("✓ Status è 'accepted' (auto-approvato per DJ)")
    else:
        print_error(f"✗ Status dovrebbe essere 'accepted', trovato: {result.get('status')}")
        return False
    
    print_info(f"Booking ID: {result['id']}")
    print_info(f"User: {result['user_name']}")
    print_info(f"Song: {result['song']}")
    
    print_success("\n✓ TEST 1 PASSED!\n")
    return True

# =============================================================================
# TEST 2: DJ Sees All Bookings
# =============================================================================

def test_dj_sees_all_bookings():
    """TEST 2: DJ vede TUTTE le prenotazioni (sia DJ che user)"""
    print_section("TEST 2: DJ Vede Tutte le Prenotazioni")
    
    # Crea più prenotazioni DJ manuali
    print_subsection("Creazione prenotazioni DJ aggiuntive")
    
    bookings_data = [
        ("Laura (DJ)", "Jovanotti - Bella - Radio Edit.mp3", "0"),
        ("Giovanni (DJ)", "Umberto Tozzi - Gloria - Original Version.mp3", "-1"),
    ]
    
    for user, song, key in bookings_data:
        data = {
            "user_name": user,
            "song": song,
            "key": key,
            "venue_id": venue_id
        }
        response = make_request("POST", "/bookings", data, use_auth=True)
        if response and response.status_code == 201:
            print_info(f"✓ Prenotazione creata: {user}")
    
    # Recupera tutte le prenotazioni
    print_subsection("Recupero prenotazioni del venue")
    response = make_request("GET", "/bookings", {"venue_id": venue_id}, use_auth=True)
    
    if not response or response.status_code != 200:
        print_error("Impossibile recuperare prenotazioni")
        return False
    
    bookings = response.json()
    
    # Conta per tipo
    dj_bookings = [b for b in bookings if b.get("session_id") is None]
    user_bookings = [b for b in bookings if b.get("session_id") is not None]
    
    print_success(f"Totale prenotazioni trovate: {len(bookings)}")
    print_info(f"  Prenotazioni DJ (session_id NULL): {len(dj_bookings)}")
    print_info(f"  Prenotazioni User (session_id UUID): {len(user_bookings)}")
    
    # Mostra dettagli
    print_subsection("Dettaglio Prenotazioni")
    for b in bookings:
        booking_type = "DJ" if b.get("session_id") is None else "USER"
        status_indicator = "✓" if b['status'] == 'accepted' else "⏳" if b['status'] == 'pending' else "✗"
        print_info(f"  [{booking_type}] {status_indicator} {b['user_name']}: {b['song'][:45]}...")
    
    if len(bookings) >= 3:
        print_success("\n✓ TEST 2 PASSED! DJ vede tutte le prenotazioni\n")
        return True
    else:
        print_error("Non abbastanza prenotazioni trovate")
        return False

# =============================================================================
# TEST 3: Session Creation (Entry Point)
# =============================================================================

def test_entry_point_creates_session():
    """TEST 3: Entry point crea sessione e fa redirect"""
    print_section("TEST 3: Entry Point - Creazione Sessione")
    
    global session_1_id, session_1_cookie
    
    print_info(f"Simulando scansione QR code: {qr_code_id}")
    
    response = make_request("GET", f"/sessions/entry/{qr_code_id}", allow_redirects=False)
    
    if response and response.status_code == 303:
        # Estrai session_id dall'URL di redirect
        location = response.headers.get("Location")
        if location:
            session_1_id = location.split("/")[-1]
        
        # Estrai cookie
        if "session_id" in response.cookies:
            session_1_cookie = {"session_id": response.cookies["session_id"]}
            print_success(f"✓ Sessione creata: {session_1_id[:8] if session_1_id else 'N/A'}...")
            print_info(f"  Redirect a: {location}")
            print_info(f"  Cookie settato: session_id")
            print_success("\n✓ TEST 3 PASSED!\n")
            return True
        else:
            print_error("Cookie session_id non settato!")
            return False
    else:
        print_error(f"Entry point fallito: {response.status_code if response else 'No response'}")
        if response:
            print_error(f"Response: {response.text}")
        return False

# =============================================================================
# TEST 4: Session Validation
# =============================================================================

def test_validate_session_success():
    """TEST 4: Validazione sessione con cookie valido"""
    print_section("TEST 4: Validazione Sessione - Successo")
    
    if not session_1_cookie:
        print_error("Nessun cookie disponibile (TEST 3 deve passare prima)")
        return False
    
    response = make_request("GET", "/sessions/validate", cookies=session_1_cookie)
    
    if response and response.status_code == 200:
        result = response.json()
        
        if result.get("valid"):
            print_success("✓ Sessione validata con successo")
            print_info(f"  DJ: {result.get('dj', {}).get('stage_name', 'N/A')}")
            
            venue_info = result.get('active_venue')
            if venue_info:
                print_info(f"  Venue attivo: {venue_info.get('name', 'N/A')}")
            else:
                print_info(f"  Venue attivo: Nessuno")
            
            print_info(f"  Tempo rimanente: {result.get('remaining_minutes', 0)} minuti")
            print_info(f"  Booking count: {result.get('booking_count', 0)}/3")
            print_success("\n✓ TEST 4 PASSED!\n")
            return True
        else:
            print_error("Sessione non valida")
            return False
    else:
        print_error("Validazione fallita")
        if response:
            print_error(f"Status: {response.status_code}")
        return False

# =============================================================================
# TEST 5: User Booking Creation (with session_id)
# =============================================================================

def test_create_user_booking_success():
    """TEST 5: User crea prenotazione (session_id deve essere collegato)"""
    print_section("TEST 5: Prenotazione Utente - Con Session")
    
    if not session_1_cookie:
        print_error("Nessuna sessione disponibile")
        return False
    
    data = {
        "user_name": "Alice (User 1)",
        "song": "Al Bano & Romina Power - Felicità.mp3",
        "key": "+1"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_1_cookie
    )
    
    if response and response.status_code == 201:
        result = response.json()
        
        # ✅ Verifica session_id presente
        if result.get("session_id"):
            print_success(f"✓ session_id presente: {result['session_id'][:20]}...")
        else:
            print_error("✗ session_id dovrebbe essere presente!")
            return False
        
        # ✅ Verifica status = pending
        if result.get("status") == "pending":
            print_success("✓ Status è 'pending' (richiede approvazione DJ)")
        else:
            print_error(f"✗ Status dovrebbe essere 'pending', trovato: {result.get('status')}")
            return False
        
        print_info(f"Booking ID: {result['id']}")
        print_info(f"User: {result['user_name']}")
        print_info(f"Song: {result['song']}")
        print_info(f"Remaining bookings: {result.get('remaining_bookings', 'N/A')}")
        
        print_success("\n✓ TEST 5 PASSED!\n")
        return True
    else:
        print_error(f"Prenotazione fallita: {response.status_code if response else 'No response'}")
        if response:
            print_error(f"Response: {response.text}")
        return False

# =============================================================================
# TEST 6: User Views Only Own Bookings
# =============================================================================

def test_get_user_bookings():
    """TEST 6: User vede SOLO le sue prenotazioni"""
    print_section("TEST 6: User Vede Solo Proprie Prenotazioni")
    
    if not session_1_cookie:
        print_error("Nessuna sessione disponibile")
        return False
    
    # Crea altre 2 prenotazioni per User 1
    print_subsection("Creazione prenotazioni aggiuntive")
    
    songs = [
        "Toto Cutugno - L'Italiano - Live Version.mp3",
        "Jovanotti - Bella - Radio Edit.mp3"
    ]
    
    for i, song in enumerate(songs, 2):
        data = {
            "user_name": f"Alice (User 1) - Booking {i}",
            "song": song,
            "key": "0"
        }
        
        response = requests.post(
            f"{BASE_URL}/bookings/user",
            params=data,
            cookies=session_1_cookie
        )
        
        if response and response.status_code == 201:
            print_info(f"✓ Prenotazione {i}/3 creata")
    
    # Recupera le prenotazioni dell'utente
    print_subsection("Recupero prenotazioni utente")
    response = requests.get(
        f"{BASE_URL}/bookings/user/my-bookings",
        cookies=session_1_cookie
    )
    
    if response and response.status_code == 200:
        result = response.json()
        bookings = result.get("bookings", [])
        
        print_success(f"✓ User vede {len(bookings)} prenotazioni")
        print_info(f"  Venue: {result.get('venue', {}).get('name', 'N/A')}")
        print_info(f"  Slot rimanenti: {result.get('remaining_slots', 'N/A')}")
        
        print_subsection("Dettaglio Prenotazioni User")
        for i, b in enumerate(bookings, 1):
            status_icon = "✓" if b['status'] == 'accepted' else "⏳" if b['status'] == 'pending' else "✗"
            print_info(f"  {i}. {status_icon} {b['user_name']}: {b['song'][:40]}...")
        
        # ✅ Verifica che siano 3 prenotazioni
        if len(bookings) == 3:
            print_success("\n✓ TEST 6 PASSED! User vede esattamente 3 prenotazioni (le sue)\n")
            return True
        else:
            print_error(f"✗ Dovrebbero essere 3 prenotazioni, trovate: {len(bookings)}")
            return False
    else:
        print_error("Impossibile ottenere prenotazioni user")
        return False

# =============================================================================
# TEST 7: Rate Limiting (Max 3 bookings per session)
# =============================================================================

def test_rate_limiting_bookings():
    """TEST 7: Rate limiting - 4a prenotazione deve essere bloccata"""
    print_section("TEST 7: Rate Limiting - Max 3 Prenotazioni")
    
    if not session_1_cookie:
        print_error("Nessuna sessione disponibile")
        return False
    
    print_info("User 1 ha già 3 prenotazioni, prova la 4a...")
    
    data = {
        "user_name": "Alice (User 1) - Booking 4",
        "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "key": "0"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_1_cookie
    )
    
    # ✅ Dovrebbe essere rifiutata con 429
    if response.status_code == 429:
        print_success("✓ 4a prenotazione correttamente bloccata (429 Too Many Requests)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 7 PASSED! Rate limiting funziona\n")
        return True
    else:
        print_error(f"✗ 4a prenotazione dovrebbe essere bloccata! Status: {response.status_code}")
        return False

# =============================================================================
# TEST 8: Second User Session (Isolation)
# =============================================================================

def test_second_user_session():
    """TEST 8: Secondo utente con sessione separata (isolamento)"""
    print_section("TEST 8: Secondo User - Isolamento Sessioni")
    
    global session_2_id, session_2_cookie
    
    # Crea sessione per User 2
    print_subsection("User 2 scansiona QR code")
    response = make_request("GET", f"/sessions/entry/{qr_code_id}", allow_redirects=False)
    
    if not response or response.status_code != 303:
        print_error("Entry point fallito per User 2")
        return False
    
    session_2_cookie = {"session_id": response.cookies.get("session_id")}
    session_2_id = response.headers.get("Location", "").split("/")[-1]
    
    print_success(f"✓ Sessione 2 creata: {session_2_id[:8] if session_2_id else 'N/A'}...")
    
    # User 2 crea una prenotazione
    print_subsection("User 2 crea prenotazione")
    data = {
        "user_name": "Bob (User 2)",
        "song": "Umberto Tozzi - Gloria - Original Version.mp3",
        "key": "-1"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_2_cookie
    )
    
    if not response or response.status_code != 201:
        print_error("User 2 non può creare prenotazione")
        return False
    
    print_success("✓ User 2 prenotazione creata")
    
    # User 2 vede le sue prenotazioni
    print_subsection("User 2 recupera le sue prenotazioni")
    response = requests.get(
        f"{BASE_URL}/bookings/user/my-bookings",
        cookies=session_2_cookie
    )
    
    if response and response.status_code == 200:
        bookings = response.json().get("bookings", [])
        
        if len(bookings) == 1:
            print_success("✓ User 2 vede solo 1 prenotazione (la sua)")
        else:
            print_error(f"✗ User 2 dovrebbe vedere 1 prenotazione, trovate: {len(bookings)}")
            return False
    
    # Verifica che User 1 veda ancora solo le sue 3
    print_subsection("Verifica isolamento User 1")
    response = requests.get(
        f"{BASE_URL}/bookings/user/my-bookings",
        cookies=session_1_cookie
    )
    
    if response and response.status_code == 200:
        bookings = response.json().get("bookings", [])
        
        if len(bookings) == 3:
            print_success("✓ User 1 vede ancora solo le sue 3 prenotazioni")
        else:
            print_error(f"✗ User 1 dovrebbe vedere 3 prenotazioni, trovate: {len(bookings)}")
            return False
    
    print_success("\n✓ TEST 8 PASSED! Utenti sono correttamente isolati\n")
    return True

# =============================================================================
# TEST 9: DJ Sees All (DJ + User 1 + User 2)
# =============================================================================

def test_dj_sees_all_including_users():
    """TEST 9: DJ vede TUTTE le prenotazioni (DJ + tutti gli user)"""
    print_section("TEST 9: DJ Vede TUTTE le Prenotazioni")
    
    response = make_request("GET", "/bookings", {"venue_id": venue_id}, use_auth=True)
    
    if not response or response.status_code != 200:
        print_error("DJ non può recuperare prenotazioni")
        return False
    
    bookings = response.json()
    
    # Conta per tipo
    dj_bookings = [b for b in bookings if b.get("session_id") is None]
    user_bookings = [b for b in bookings if b.get("session_id") is not None]
    
    print_success(f"DJ vede {len(bookings)} prenotazioni totali")
    print_info(f"  DJ manual (session_id NULL): {len(dj_bookings)}")
    print_info(f"  User bookings (session_id UUID): {len(user_bookings)}")
    
    # Mostra dettagli
    print_subsection("Tutte le Prenotazioni (Vista DJ)")
    for b in bookings:
        booking_type = "DJ" if b.get("session_id") is None else "USER"
        status_icon = "✓" if b['status'] == 'accepted' else "⏳" if b['status'] == 'pending' else "✗"
        print_info(f"  [{booking_type:5}] {status_icon} {b['user_name']:30} | {b['song'][:35]}")
    
    # Verifica: dovremmo avere 3 DJ + 3 User1 + 1 User2 = 7 totali
    expected_total = 3 + 3 + 1
    if len(bookings) >= expected_total:
        print_success(f"\n✓ TEST 9 PASSED! DJ vede tutte le prenotazioni (≥{expected_total})\n")
        return True
    else:
        print_warning(f"Trovate {len(bookings)} prenotazioni, attese almeno {expected_total}")
        return False
    
# =============================================================================
# TEST: Ricerca canzone nel catalogo
# =============================================================================

def test_public_catalog_search():
    """TEST 11: Ricerca nel catalogo pubblico"""
    print_section("TEST 11: Ricerca Catalogo Pubblico")
    
    response = requests.get(
        f"{BASE_URL}/songs/public/{qr_code_id}",
        params={"search": "bella"},
        cookies=session_2_cookie
    )
    
    if response and response.status_code == 200:
        result = response.json()
        songs = result.get("songs", [])
        
        print_success(f"Ricerca funzionante")
        print_info(f"Trovate {len(songs)} canzoni con 'bella'")
        
        for song in songs:
            print_info(f"  - {song}")
        
        return True
    else:
        print_error("Ricerca fallita")
        return False

# =============================================================================
# TEST 10: DJ Accept/Reject User Bookings
# =============================================================================

def test_dj_accept_reject_bookings():
    """TEST 10: DJ accetta e rifiuta prenotazioni user"""
    print_section("TEST 10: DJ Accetta/Rifiuta Prenotazioni User")
    
    # Recupera prenotazioni pending
    print_subsection("Recupero prenotazioni pending")
    response = make_request("GET", "/bookings", {"venue_id": venue_id}, use_auth=True)
    
    if not response or response.status_code != 200:
        print_error("Impossibile recuperare prenotazioni")
        return False
    
    bookings = response.json()
    pending = [b for b in bookings if b['status'] == 'pending']
    
    print_info(f"Prenotazioni pending: {len(pending)}")
    
    if len(pending) < 2:
        print_warning("Non abbastanza prenotazioni pending per testare")
        return None  # Skip
    
    # Accetta la prima
    print_subsection(f"Accettazione prenotazione #{pending[0]['id']}")
    response = make_request("POST", f"/bookings/{pending[0]['id']}/accept", use_auth=True)
    
    if response and response.status_code == 200:
        result = response.json()
        print_success(f"✓ Prenotazione accettata")
        print_info(f"  Messaggio: {result.get('message', 'N/A')}")
    else:
        print_error("Accettazione fallita")
        return False
    
    # Rifiuta la seconda
    print_subsection(f"Rifiuto prenotazione #{pending[1]['id']}")
    response = make_request("POST", f"/bookings/{pending[1]['id']}/reject", use_auth=True)
    
    if response and response.status_code == 200:
        result = response.json()
        print_success(f"✓ Prenotazione rifiutata")
        print_info(f"  Messaggio: {result.get('message', 'N/A')}")
    else:
        print_error("Rifiuto fallito")
        return False
    
    print_success("\n✓ TEST 10 PASSED! DJ può gestire prenotazioni\n")
    return True

# =============================================================================
# NEGATIVE TESTS - Test scenari di errore
# =============================================================================

def test_invalid_qr_code():
    """TEST 11a: Entry point con QR code inesistente (NEGATIVO)"""
    print_section("TEST 11a: Entry Point - QR Code Inesistente (NEGATIVO)")
    
    fake_qr = "DJ-FAKE-NONEXISTENT-2024"
    response = make_request("GET", f"/sessions/entry/{fake_qr}", allow_redirects=False)
    
    if response.status_code == 404:
        print_success("✓ QR code inesistente correttamente rifiutato (404)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 11a PASSED! Entry point rifiuta QR invalidi\n")
        return True
    else:
        print_error(f"✗ QR code inesistente dovrebbe dare 404, ricevuto: {response.status_code if response else 'No response'}")
        return False

def test_validate_session_without_cookie():
    """TEST 11b: Validazione sessione senza cookie (NEGATIVO)"""
    print_section("TEST 11b: Validazione Sessione - Senza Cookie (NEGATIVO)")
    
    # Nessun cookie inviato
    response = make_request("GET", "/sessions/validate", cookies=None)
    
    if response.status_code == 401:
        result = response.json()
        detail = result.get("detail", "")
        if "Sessione non trovata" in detail and "QR code" in detail:
            print_success("✓ Validazione senza cookie correttamente rifiutata (401)")
            print_info(f"  Messaggio: {detail}")
            print_success("\n✓ TEST 11b PASSED! Sessione richiede cookie\n")
            return True
    
    print_error(f"✗ Validazione senza cookie dovrebbe dare 401, ricevuto: {response.status_code if response else 'No response'}")
    return False

def test_validate_session_invalid_cookie():
    """TEST 11c: Validazione con cookie session_id invalido (NEGATIVO)"""
    print_section("TEST 11c: Validazione Sessione - Cookie Invalido (NEGATIVO)")
    
    fake_cookie = {"session_id": "fake-invalid-uuid-12345"}
    response = make_request("GET", "/sessions/validate", cookies=fake_cookie)
    
    if response.status_code == 401:
        result = response.json()
        detail = result.get("detail", "")
        if "Sessione non trovata" in detail:
            print_success("✓ Cookie session_id invalido correttamente rifiutato (401)")
            print_info(f"  Messaggio: {detail}")
            print_success("\n✓ TEST 11c PASSED! Cookie invalido rifiutato\n")
            return True
    
    print_error(f"✗ Cookie invalido dovrebbe dare 401, ricevuto: {response.status_code if response else 'No response'}")
    return False

def test_user_booking_without_cookie():
    """TEST 11d: Prenotazione user senza sessione (NEGATIVO)"""
    print_section("TEST 11d: Prenotazione User - Senza Cookie (NEGATIVO)")
    
    data = {
        "user_name": "Hacker Test",
        "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "key": "0"
    }
    
    # Nessun cookie
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=None
    )
    
    if response.status_code == 401:
        print_success("✓ Prenotazione senza sessione correttamente rifiutata (401)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 11d PASSED! Prenotazioni richiedono sessione\n")
        return True
    else:
        print_error(f"✗ Prenotazione senza sessione dovrebbe dare 401, ricevuto: {response.status_code}")
        return False

def test_user_booking_nonexistent_song():
    """TEST 11e: Prenotazione canzone inesistente (NEGATIVO)"""
    print_section("TEST 11e: Prenotazione User - Canzone Inesistente (NEGATIVO)")
    
    if not session_1_cookie:
        print_warning("Skipping: nessuna sessione disponibile")
        return None
    
    data = {
        "user_name": "Alice Test",
        "song": "Canzone Che Non Esiste Nel Catalogo.mp3",
        "key": "0"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_2_cookie
    )
    
    if response.status_code == 404:
        print_success("✓ Canzone inesistente correttamente rifiutata (404)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 11e PASSED! Solo canzoni nel catalogo sono accettate\n")
        return True
    else:
        print_error(f"✗ Canzone inesistente dovrebbe dare 404, ricevuto: {response.status_code}")
        return False

def test_user_booking_venue_inactive():
    """TEST 11f: Prenotazione con venue inattivo (NEGATIVO)"""
    print_section("TEST 11f: Prenotazione User - Venue Inattivo (NEGATIVO)")
    
    if not session_2_cookie or not venue_id:
        print_warning("Skipping: mancano prerequisiti")
        return None
    
    # Prima disattiva il venue
    print_subsection("Disattivazione venue")
    response = make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    
    if not response or response.status_code != 200:
        print_error("Impossibile disattivare venue")
        return False
    
    print_info("✓ Venue disattivato")
    
    # Prova a prenotare
    print_subsection("Tentativo prenotazione con venue inattivo")
    data = {
        "user_name": "Alice Test",
        "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "key": "0"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_2_cookie
    )
    
    should_be_rejected = response.status_code == 400
    
    # Riattiva il venue per test successivi
    print_subsection("Riattivazione venue")
    make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    
    if should_be_rejected:
        print_success("✓ Prenotazione con venue inattivo correttamente rifiutata (400)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 11f PASSED! Venue deve essere attivo per prenotazioni\n")
        return True
    else:
        print_error(f"✗ Prenotazione con venue inattivo dovrebbe dare 400, ricevuto: {response.status_code if response else 'No response'}")
        return False

def test_dj_unauthorized_access():
    """TEST 11g: Accesso endpoint DJ senza autenticazione (NEGATIVO)"""
    print_section("TEST 11g: Accesso DJ - Senza Autenticazione (NEGATIVO)")
    
    # Prova a recuperare prenotazioni senza token JWT
    print_subsection("Tentativo accesso bookings DJ senza token")
    response = make_request("GET", "/bookings", {"venue_id": venue_id}, use_auth=False)
    
    if response.status_code == 403:
        print_success("✓ Accesso bookings DJ senza auth correttamente rifiutato (403)")
    else:
        print_error(f"✗ Accesso non autorizzato dovrebbe dare 403, ricevuto: {response.status_code}")
        return False
    
    # Prova a creare venue senza token
    print_subsection("Tentativo creazione venue senza token")
    data = {"name": "Hacker Venue", "address": "Via Hacker 123"}
    response = make_request("POST", "/venues", data, use_auth=False)
    
    if response.status_code == 403:
        print_success("✓ Creazione venue senza auth correttamente rifiutata (403)")
        print_success("\n✓ TEST 11g PASSED! Endpoint DJ sono protetti\n")
        return True
    else:
        print_error(f"✗ Creazione venue non autorizzata dovrebbe dare 403, ricevuto: {response.status_code}")
        return False

def test_dj_access_wrong_venue():
    """TEST 11i: DJ tenta di accedere a venue di altro DJ (NEGATIVO)"""
    print_section("TEST 11i: DJ Accesso Venue Altrui (NEGATIVO)")
    
    # Tenta di recuperare bookings di un venue inesistente/non suo
    fake_venue_id = 99999
    response = make_request("GET", "/bookings", {"venue_id": fake_venue_id}, use_auth=True)
    
    if response.status_code == 404:
        print_success("✓ Accesso a venue non proprio correttamente rifiutato (404)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 11i PASSED! DJ può accedere solo ai propri venue\n")
        return True
    else:
        print_error(f"✗ Accesso venue altrui dovrebbe dare 404, ricevuto: {response.status_code}")
        return False

def test_session_expiry_real():
    """TEST 11j: Test reale sessione scaduta con modifica DB (NEGATIVO)"""
    print_section("TEST 11j: Sessione Scaduta - Test Reale con DB (NEGATIVO)")
    
    import time
    
    # Step 1: Crea terza sessione
    print_subsection("1. Creazione terza sessione")
    response = make_request("GET", f"/sessions/entry_fake/{qr_code_id}", allow_redirects=False)
    
    if not response or response.status_code != 303:
        print_error("Impossibile creare terza sessione")
        return False
    
    session_3_cookie = {"session_id": response.cookies.get("session_id")}
    session_3_id = response.headers.get("Location", "").split("/")[-1]
    
    print_success(f"✓ Terza sessione creata: {session_3_id[:8] if session_3_id else 'N/A'}...")
    print_info(f"📋 Session ID completo: {session_3_id}")
    
    # Step 2: Verifica sessione valida
    print_subsection("2. Verifica sessione inizialmente valida")
    response = make_request("GET", "/sessions/validate", cookies=session_3_cookie)
    
    if response and response.status_code == 200:
        result = response.json()
        if result.get("valid"):
            print_success("✓ Sessione inizialmente valida")
        else:
            print_error("✗ Sessione dovrebbe essere inizialmente valida")
            return False
    else:
        print_error("Validazione iniziale fallita")
        return False
    
    # Step 4: Aspetta scadenza
    print_subsection("4. Attesa scadenza sessione")
    print_info("⏱️  Aspettando 6 secondi per scadenza...")
    
    for i in range(6, 0, -1):
        print_info(f"   {i} secondi rimanenti...")
        time.sleep(1)
    
    print_info("⏰ Sessione dovrebbe essere scaduta!")
    
    # Step 5: Testa validazione (ora dovrebbe dare 401)
    print_subsection("5. Test validazione sessione scaduta")
    response = make_request("GET", "/sessions/validate", cookies=session_3_cookie)
    
    if response.status_code == 401:  # 🆕 Cambiato da 200 a 401
        detail = response.json().get("detail", "")
        if "scaduta" in detail:
            print_success("✓ Sessione correttamente rilevata come scaduta (401)")
            print_info(f"  Messaggio: {detail}")
            
            # Step 6: Test prenotazione
            print_subsection("6. Test prenotazione con sessione scaduta")
            data = {
                "user_name": "Charlie (Scaduto)",
                "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
                "key": "0"
            }
            
            response = requests.post(
                f"{BASE_URL}/bookings/user",
                params=data,
                cookies=session_3_cookie
            )
            
            if response.status_code == 401:
                print_success("✓ Prenotazione con sessione scaduta rifiutata (401)")
                print_success("\n✓ TEST 11j PASSED! Gestione scadenza funziona\n")
                return True
            else:
                print_error(f"✗ Prenotazione dovrebbe essere rifiutata (401), ricevuto: {response.status_code}")
                return False
        else:
            print_error(f"✗ Messaggio di errore inaspettato: {detail}")
            return False
    elif response and response.status_code == 200:
        result = response.json()
        if result.get("valid"):
            print_warning("⚠️  Sessione ancora valida")
            print_info(f"  Tempo rimanente: {result.get('remaining_minutes', 'N/A')} min")
            print_warning("\n⚠️  TEST 11j FAILED - Backend non gestisce scadenza automatica\n")
            return False
    else:
        print_error(f"✗ Comportamento inaspettato: {response.status_code if response else 'No response'}")
        return False

def test_venue_change_invalidates_session():
    """TEST 14: Cambio venue invalida sessioni esistenti (COMPORTAMENTO)"""
    print_section("TEST 14: Cambio Venue Invalida Sessioni Esistenti")
    
    global venue_id
    
    # 1. User scansiona QR con Venue A attivo
    print_subsection("1. User scansiona QR con Venue A attivo")
    response = make_request("GET", f"/sessions/entry/{qr_code_id}", allow_redirects=False)
    
    if not response or response.status_code != 303:
        print_error("Impossibile creare sessione test")
        return False
    
    venue_a_session_cookie = {"session_id": response.cookies.get("session_id")}
    print_success("✓ Sessione creata per Venue A")
    
    # 2. Verifica sessione valida
    print_subsection("2. Verifica sessione inizialmente valida")
    response = make_request("GET", "/sessions/validate", cookies=venue_a_session_cookie)
    
    if response and response.status_code == 200:
        result = response.json()
        if result.get("valid"):
            print_success("✓ Sessione valida per Venue A")
            venue_a_name = result.get("active_venue", {}).get("name", "N/A")
            print_info(f"  Venue A: {venue_a_name}")
        else:
            print_error("✗ Sessione dovrebbe essere valida")
            return False
    else:
        print_error("Validazione sessione fallita")
        return False
    
    # 3. DJ crea e attiva nuovo venue (Venue B)
    print_subsection("3. DJ crea e attiva Venue B")
    venue_b_data = {"name": "Venue B Test", "address": "Via B 123", "capacity": 150}
    response = make_request("POST", "/venues", venue_b_data, use_auth=True)
    
    if not response or response.status_code != 201:
        print_error("Impossibile creare Venue B")
        return False
    
    venue_b_id = response.json()["id"]
    print_success(f"✓ Venue B creato: ID {venue_b_id}")
    
    # Attiva Venue B (questo disattiva automaticamente Venue A)
    response = make_request("POST", f"/venues/{venue_b_id}/toggle", use_auth=True)
    
    if response and response.status_code == 200:
        print_success("✓ Venue B attivato (Venue A automaticamente disattivato)")
    else:
        print_error("Impossibile attivare Venue B")
        return False
    
    # 4. Verifica sessione ora invalida (ora riceve 400 invece di 200)
    print_subsection("4. Verifica sessione Venue A ora invalida")
    response = make_request("GET", "/sessions/validate", cookies=venue_a_session_cookie)
    
    if response.status_code == 400:  # 🆕 Cambiato da 200 a 400
        result = response.json()
        detail = result.get("detail", "")
        
        if "locale non è più attivo" in detail and "cambiato locale" in detail:
            print_success("✓ Sessione Venue A correttamente invalidata (400)")
            print_info(f"  Messaggio: {detail}")
        else:
            print_error(f"✗ Messaggio di errore inaspettato: {detail}")
            return False
    else:
        print_error(f"✗ Sessione dovrebbe essere invalida (400), ricevuto: {response.status_code}")
        return False
    
    # 5. Verifica prenotazione rifiutata con sessione Venue A
    print_subsection("5. Verifica prenotazione rifiutata con sessione invalida")
    data = {
        "user_name": "Test Venue Change",
        "song": "Domenico Modugno - Volare - Nel Blu Dipinto di Blu.mp3",
        "key": "0"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=venue_a_session_cookie
    )
    
    if response.status_code == 400:
        detail = response.json().get("detail", "")
        if "locale della tua sessione non è più attivo" in detail:
            print_success("✓ Prenotazione correttamente rifiutata per venue inattivo")
            print_info(f"  Messaggio: {detail}")
        else:
            print_error(f"✗ Messaggio di errore inaspettato: {detail}")
            return False
    else:
        print_error(f"✗ Prenotazione dovrebbe essere rifiutata (400), ricevuto: {response.status_code}")
        return False
    
    # 6. Verifica nuovo user può creare sessione per Venue B
    print_subsection("6. Verifica nuovo user può accedere a Venue B")
    response = make_request("GET", f"/sessions/entry/{qr_code_id}", allow_redirects=False)
    
    if response and response.status_code == 303:
        venue_b_session_cookie = {"session_id": response.cookies.get("session_id")}
        
        # Valida nuova sessione
        response = make_request("GET", "/sessions/validate", cookies=venue_b_session_cookie)
        
        if response and response.status_code == 200:
            result = response.json()
            if result.get("valid"):
                venue_name = result.get("active_venue", {}).get("name", "N/A")
                print_success(f"✓ Nuova sessione valida per: {venue_name}")
            else:
                print_error("✗ Nuova sessione dovrebbe essere valida per Venue B")
                return False
        else:
            print_error("Validazione nuova sessione fallita")
            return False
    else:
        print_error("Impossibile creare nuova sessione per Venue B")
        return False
    
    print_success("\n✓ TEST 14 PASSED! Cambio venue invalida correttamente le sessioni esistenti\n")
    return True

def test_user_can_delete_own_booking():
    """TEST 13a: User può cancellare propria prenotazione pending (POSITIVO)"""
    print_section("TEST 13a: User Cancella Propria Prenotazione - Successo")
    
    if not session_2_cookie:  # Usa session 2 che ha ancora slot
        print_warning("Skipping: nessuna sessione 2 disponibile")
        return None
    
    # 1. Crea una prenotazione
    print_subsection("1. Creazione prenotazione da cancellare")
    data = {
        "user_name": "Bob Delete Test",
        "song": "Toto Cutugno - L'Italiano - Live Version.mp3",
        "key": "+1"
    }
    
    venue_id = 1
    print_subsection("3. Attivazione Venue ")
    response = make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_2_cookie
    )
    
    if not response or response.status_code != 201:
        print_error("Impossibile creare prenotazione test")
        return False
    
    booking_to_delete = response.json()
    booking_id = booking_to_delete["id"]
    print_success(f"✓ Prenotazione creata: ID {booking_id}")
    
    # 2. Verifica lista prenotazioni (dovrebbe averne 2 ora)
    response = requests.get(
        f"{BASE_URL}/bookings/user/my-bookings",
        cookies=session_2_cookie
    )
    
    if response and response.status_code == 200:
        bookings_before = response.json()["bookings"]
        print_info(f"  Prenotazioni prima: {len(bookings_before)}")
    
    # 3. Cancella la prenotazione
    print_subsection("2. Cancellazione prenotazione")
    response = requests.delete(
        f"{BASE_URL}/bookings/user/{booking_id}",
        cookies=session_2_cookie
    )
    
    if response and response.status_code == 200:
        result = response.json()
        print_success("✓ Prenotazione cancellata con successo")
        print_info(f"  Messaggio: {result.get('message', 'N/A')}")
        print_info(f"  Slot disponibili: {result.get('available_slots', 'N/A')}")
        print_info(f"  Prenotazioni rimanenti: {result.get('remaining_bookings', 'N/A')}")
    else:
        print_error(f"✗ Cancellazione fallita: {response.status_code if response else 'No response'}")
        return False
    
    # 4. Verifica lista aggiornata
    print_subsection("3. Verifica lista aggiornata")
    response = requests.get(
        f"{BASE_URL}/bookings/user/my-bookings",
        cookies=session_2_cookie
    )
    
    if response and response.status_code == 200:
        bookings_after = response.json()["bookings"]
        
        if len(bookings_after) == len(bookings_before) - 1:
            print_success(f"✓ Lista aggiornata: {len(bookings_after)} prenotazioni")
            
            # Verifica che la prenotazione cancellata non ci sia più
            deleted_found = any(b["id"] == booking_id for b in bookings_after)
            if not deleted_found:
                print_success("✓ Prenotazione cancellata non più presente in lista")
                print_success("\n✓ TEST 13a PASSED! Cancellazione prenotazione funziona\n")
                return True
            else:
                print_error("✗ Prenotazione cancellata ancora presente in lista")
                return False
        else:
            print_error(f"✗ Lista non aggiornata: attese {len(bookings_before)-1}, trovate {len(bookings_after)}")
            return False
    
    return False

def test_user_cannot_delete_others_booking():
    """TEST 13b: User non può cancellare prenotazioni altrui (NEGATIVO)"""
    print_section("TEST 13b: User Non Può Cancellare Prenotazioni Altrui (NEGATIVO)")
    
    if not session_1_cookie or not session_2_cookie:
        print_warning("Skipping: servono entrambe le sessioni")
        return None
    
    # 1. Session 1 crea una prenotazione  
    print_subsection("1. Session 4 crea prenotazione")
    data = {
        "user_name": "Alice Protected",
        "song": "Umberto Tozzi - Gloria - Original Version.mp3", 
        "key": "0"
    }
    
    # Nota: session_1 potrebbe essere al limite, creiamo una nuova sessione
    response = make_request("GET", f"/sessions/entry/{qr_code_id}", allow_redirects=False)
    if response and response.status_code == 303:
        session_4_cookie = {"session_id": response.cookies.get("session_id")}
        
        response = requests.post(
            f"{BASE_URL}/bookings/user",
            params=data,
            cookies=session_4_cookie
        )
        
        if response and response.status_code == 201:
            protected_booking_id = response.json()["id"]
            print_success(f"✓ Prenotazione protetta creata: ID {protected_booking_id}")
        else:
            print_warning("Impossibile creare prenotazione protetta")
            return None
        
        # 2. Session 2 tenta di cancellare prenotazione di Session 1
        print_subsection("2. Session 2 tenta cancellazione non autorizzata")
        response = requests.delete(
            f"{BASE_URL}/bookings/user/{protected_booking_id}",
            cookies=session_2_cookie
        )
        
        if response.status_code == 404:
            print_success("✓ Cancellazione non autorizzata correttamente rifiutata (404)")
            print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
            print_success("\n✓ TEST 13b PASSED! Protezione prenotazioni altrui funziona\n")
            return True
        else:
            print_error(f"✗ Cancellazione dovrebbe essere rifiutata (404), ricevuto: {response.status_code}")
            return False

def test_user_cannot_delete_with_venue_inactive():
    """TEST 13c: User non può cancellare con venue inattivo (NEGATIVO)"""  
    print_section("TEST 13c: Cancellazione con Venue Inattivo (NEGATIVO)")
    
    if not session_2_cookie or not venue_id:
        print_warning("Skipping: mancano prerequisiti")
        return None
    
    # 1. Crea prenotazione
    print_subsection("1. Creazione prenotazione")
    data = {
        "user_name": "Bob Venue Test",
        "song": "Al Bano & Romina Power - Felicità.mp3",
        "key": "0"
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings/user",
        params=data,
        cookies=session_2_cookie
    )
    
    if not response or response.status_code != 201:
        print_warning("Impossibile creare prenotazione test")
        return None
        
    booking_id = response.json()["id"]
    
    # 2. DJ disattiva venue
    print_subsection("2. DJ disattiva venue")
    response = make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    print_info("✓ Venue disattivato")
    
    # 3. User tenta cancellazione
    print_subsection("3. Tentativo cancellazione con venue inattivo")
    response = requests.delete(
        f"{BASE_URL}/bookings/user/{booking_id}",
        cookies=session_2_cookie
    )
    
    # 4. Riattiva venue per test successivi
    make_request("POST", f"/venues/{venue_id}/toggle", use_auth=True)
    print_info("✓ Venue riattivato")
    
    if response.status_code == 400:
        print_success("✓ Cancellazione con venue inattivo correttamente rifiutata (400)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 13c PASSED! Protezione venue inattivo funziona\n")
        return True
    else:
        print_error(f"✗ Cancellazione dovrebbe essere rifiutata (400), ricevuto: {response.status_code}")
        return False

def test_user_delete_booking_invalid_id():
    """TEST 13d: Cancellazione con ID inesistente (NEGATIVO)"""
    print_section("TEST 13d: Cancellazione ID Inesistente (NEGATIVO)")
    
    if not session_2_cookie:
        print_warning("Skipping: nessuna sessione disponibile")
        return None
    
    fake_booking_id = 99999
    response = requests.delete(
        f"{BASE_URL}/bookings/user/{fake_booking_id}",
        cookies=session_2_cookie
    )
    
    if response.status_code == 404:
        print_success("✓ ID inesistente correttamente rifiutato (404)")
        print_info(f"  Messaggio: {response.json().get('detail', 'N/A')}")
        print_success("\n✓ TEST 13d PASSED! Validazione ID funziona\n")
        return True
    else:
        print_error(f"✗ ID inesistente dovrebbe dare 404, ricevuto: {response.status_code}")
        return False

def test_get_dj_profile_info():
    """TEST 15a: Ottenere informazioni profilo DJ (POSITIVO)"""
    print_section("TEST 15a: Get DJ Profile Info - Successo")
    
    if not token:
        print_warning("Skipping: nessun token disponibile")
        return None
    
    response = make_request("GET", "/auth/me", use_auth=True)
    
    if response and response.status_code == 200:
        result = response.json()
        
        # Verifica campi obbligatori
        required_fields = ["id", "full_name", "stage_name", "email", "qr_code_id"]
        for field in required_fields:
            if field not in result:
                print_error(f"✗ Campo mancante: {field}")
                return False
        
        print_success("✓ Profilo DJ recuperato correttamente")
        print_info(f"  ID: {result.get('id')}")
        print_info(f"  Nome: {result.get('full_name')}")
        print_info(f"  Stage Name: {result.get('stage_name')}")
        print_info(f"  Email: {result.get('email')}")
        print_info(f"  QR Code: {result.get('qr_code_id')}")
        print_info(f"  Phone: {result.get('phone', 'N/A')}")
        
        # Verifica che password_hash NON sia presente
        if "password_hash" in result:
            print_error("✗ password_hash non dovrebbe essere esposta")
            return False
        
        print_success("\n✓ TEST 15a PASSED! Get profilo DJ funziona\n")
        return True
    else:
        print_error(f"✗ Get profilo fallito: {response.status_code if response else 'No response'}")
        return False

def test_get_dj_profile_without_auth():
    """TEST 15b: Get profilo senza autenticazione (NEGATIVO)"""
    print_section("TEST 15b: Get DJ Profile - Senza Auth (NEGATIVO)")
    
    response = make_request("GET", "/auth/me", use_auth=False)
    
    if response.status_code == 403:
        print_success("✓ Get profilo senza auth correttamente rifiutato (403)")
        print_success("\n✓ TEST 15b PASSED! Protezione auth funziona\n")
        return True
    else:
        print_error(f"✗ Get profilo dovrebbe dare 403, ricevuto: {response.status_code}")
        return False

def test_update_dj_profile_success():
    """TEST 15c: Update profilo DJ con successo (POSITIVO)"""
    print_section("TEST 15c: Update DJ Profile - Successo")
    
    if not token:
        print_warning("Skipping: nessun token disponibile")
        return None
    
    # Dati di aggiornamento
    update_data = {
        "full_name": "Mario Rossi Updated",
        "stage_name": "DJ Mario Pro", 
        "phone": "+39 333 9876543"
        # Non aggiorniamo email per evitare conflitti
    }
    
    response = make_request("PUT", "/auth/me", update_data, use_auth=True)
    
    if response and response.status_code == 200:
        result = response.json()
        
        # Verifica aggiornamenti applicati
        if (result.get("full_name") == update_data["full_name"] and
            result.get("stage_name") == update_data["stage_name"] and 
            result.get("phone") == update_data["phone"]):
            
            print_success("✓ Profilo DJ aggiornato correttamente")
            print_info(f"  Nome: {result.get('full_name')}")
            print_info(f"  Stage Name: {result.get('stage_name')}")
            print_info(f"  Phone: {result.get('phone')}")
            
            print_success("\n✓ TEST 15c PASSED! Update profilo DJ funziona\n")
            return True
        else:
            print_error("✗ Dati non aggiornati correttamente")
            return False
    else:
        print_error(f"✗ Update profilo fallito: {response.status_code if response else 'No response'}")
        return False

def test_update_dj_profile_duplicate_email():
    """TEST 15d: Update con email già esistente (NEGATIVO)"""
    print_section("TEST 15d: Update DJ Profile - Email Duplicata (NEGATIVO)")
    
    if not token:
        print_warning("Skipping: nessun token disponibile")
        return None
    
    # Tenta aggiornamento con email che potrebbe esistere
    update_data = {
        "email": "test_123456@karaokati.com"  # Email potenzialmente esistente
    }
    
    response = make_request("PUT", "/auth/me", update_data, use_auth=True)
    
    # Potrebbe dare 400 se email esiste o 200 se non esiste
    if response.status_code in [200, 400]:
        if response.status_code == 400:
            detail = response.json().get("detail", "")
            if "già utilizzata" in detail:
                print_success("✓ Email duplicata correttamente rifiutata (400)")
                print_info(f"  Messaggio: {detail}")
                print_success("\n✓ TEST 15d PASSED! Validazione email funziona\n")
                return True
        elif response.status_code == 200:
            print_success("✓ Email aggiornata (non era duplicata)")
            print_success("\n✓ TEST 15d PASSED! Update email funziona\n")
            return True
    
    print_error(f"✗ Comportamento inaspettato: {response.status_code}")
    return False

def test_change_password_success():
    """TEST 15e: Cambio password con successo (POSITIVO)"""
    print_section("TEST 15e: Change Password - Successo")
    
    if not token:
        print_warning("Skipping: nessun token disponibile")
        return None
    
    password_data = {
        "current_password": "password123",  # Password usata nella registrazione
        "new_password": "newpassword456"
    }
    
    response = make_request("PUT", "/auth/change-password", password_data, use_auth=True)
    
    if response and response.status_code == 200:
        result = response.json()
        
        if "modificata con successo" in result.get("message", ""):
            print_success("✓ Password cambiata correttamente")
            print_info(f"  Messaggio: {result.get('message')}")
            
            print_success("\n✓ TEST 15e PASSED! Cambio password funziona\n")
            return True
        else:
            print_error("✗ Messaggio di successo non trovato")
            return False
    else:
        print_error(f"✗ Cambio password fallito: {response.status_code if response else 'No response'}")
        return False

def test_change_password_wrong_current():
    """TEST 15f: Cambio password con password attuale errata (NEGATIVO)"""
    print_section("TEST 15f: Change Password - Password Attuale Errata (NEGATIVO)")
    
    if not token:
        print_warning("Skipping: nessun token disponibile")
        return None
    
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword789"
    }
    
    response = make_request("PUT", "/auth/change-password", password_data, use_auth=True)
    
    if response.status_code == 400:
        detail = response.json().get("detail", "")
        if "Password attuale non corretta" in detail:
            print_success("✓ Password errata correttamente rifiutata (400)")
            print_info(f"  Messaggio: {detail}")
            print_success("\n✓ TEST 15f PASSED! Validazione password funziona\n")
            return True
    
    print_error(f"✗ Password errata dovrebbe dare 400, ricevuto: {response.status_code}")
    return False

def test_logout_without_auth():
    """TEST 15h: Logout senza autenticazione (NEGATIVO)"""
    print_section("TEST 15h: Logout - Senza Auth (NEGATIVO)")
    
    response = make_request("POST", "/auth/logout", use_auth=False)
    
    if response.status_code == 403:
        print_success("✓ Logout senza auth correttamente rifiutato (403)")
        print_success("\n✓ TEST 15h PASSED! Protezione logout funziona\n")
        return True
    else:
        print_error(f"✗ Logout dovrebbe dare 403, ricevuto: {response.status_code}")
        return False

def test_change_password_and_login():
    """TEST 15i: Cambio password e login con nuova (COMPLETO)"""
    print_section("TEST 15i: Cambio Password + Login Nuova - Workflow Completo")
    
    # Crea un NUOVO DJ per questo test (così non interferiamo con quello globale)
    print_subsection("1. Registrazione DJ per test password")
    
    new_dj_data = {
        "full_name": "Test Password DJ",
        "stage_name": "DJ Password Test", 
        "email": f"password_test_{int(time.time())}@karaokati.com",
        "phone": "+39 333 1111111",
        "password": "original_password_123"
    }
    
    response = make_request("POST", "/auth/register", new_dj_data)
    
    if not response or response.status_code != 201:
        print_error("Impossibile registrare DJ test")
        return False
    
    test_token = response.json().get("token")
    test_email = new_dj_data["email"]
    
    print_success(f"✓ DJ test registrato: {test_email}")
    
    # Step 2: Cambia password
    print_subsection("2. Cambio password DJ test")
    
    password_data = {
        "current_password": "original_password_123",
        "new_password": "new_password_456"
    }
    
    headers = {"Authorization": f"Bearer {test_token}"}
    response = requests.put(
        f"{BASE_URL}/auth/change-password",
        json=password_data,
        headers=headers
    )
    
    if not response or response.status_code != 200:
        print_error("Cambio password fallito")
        return False
    
    print_success("✓ Password cambiata con successo")
    
    # Step 3: Login con nuova password
    print_subsection("3. Login con nuova password")
    
    login_data = {
        "email": test_email,
        "password": "new_password_456"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    
    if response and response.status_code == 200:
        result = response.json()
        new_token = result.get("token")
        
        print_success("✓ Login con nuova password riuscito")
        print_info(f"  Nuovo token: {new_token[:30]}...")
        
        # Step 4: Verifica che vecchia password NON funzioni
        print_subsection("4. Verifica vecchia password non funziona")
        
        old_login_data = {
            "email": test_email,
            "password": "original_password_123"  # Vecchia password
        }
        
        response = make_request("POST", "/auth/login", old_login_data)
        
        if response.status_code == 401:
            print_success("✓ Vecchia password correttamente rifiutata")
            print_success("\n✓ TEST 15i PASSED! Workflow cambio password completo\n")
            return True
        else:
            print_error("✗ Vecchia password dovrebbe essere rifiutata")
            return False
    else:
        print_error("✗ Login con nuova password fallito")
        return False

# =============================================================================
# TEST 12: Cleanup
# =============================================================================

def test_cleanup():
    """TEST 12: Cleanup ambiente test"""
    print_section("TEST 12: Cleanup Dati Test")
    
    # Elimina venue (cascade elimina bookings)
    if venue_id:
        print_subsection("Eliminazione venue")
        response = make_request("DELETE", f"/venues/{venue_id}", use_auth=True)
        if response and response.status_code == 200:
            print_success("✓ Venue eliminato (bookings eliminati in cascade)")
    
    # Elimina catalogo
    print_subsection("Eliminazione catalogo canzoni")
    response = make_request("DELETE", "/songs", use_auth=True)
    if response and response.status_code == 200:
        result = response.json()
        print_success(f"✓ {result['deleted']} canzoni eliminate")
    
    print_success("\n✓ TEST 12 PASSED! Cleanup completato\n")
    return True

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_complete_booking_tests():
    """Run complete booking test suite including negative tests"""
    print(f"\n{Colors.PURPLE}{'='*70}")
    print(f"  🧪 KARAOKATI COMPLETE BOOKING SYSTEM TEST SUITE")
    print(f"  Base URL: {BASE_URL}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Setup
    if not setup_dj_and_venue():
        print_error("Setup fallito, impossibile continuare")
        return
    
    tests = [
        # === POSITIVE TESTS ===
        # DJ Bookings
        ("DJ Manual Booking (NULL)", test_dj_manual_booking_null_session),
        ("DJ Vede Tutte le Prenotazioni", test_dj_sees_all_bookings),
        
        # Sessions
        ("Entry Point Crea Sessione", test_entry_point_creates_session),
        ("Validazione Sessione", test_validate_session_success),
        
        # User Bookings
        ("User Booking Con Session", test_create_user_booking_success),
        ("User Vede Solo Proprie", test_get_user_bookings),
        ("Rate Limiting (Max 3)", test_rate_limiting_bookings),
        
        # Multi-User
        ("Secondo User - Isolamento", test_second_user_session),
        ("DJ Vede Tutti (DJ+Users)", test_dj_sees_all_including_users),
        
		#User
        ("Ricerca Catalogo Pubblico", test_public_catalog_search),
        
        # DJ Management
        ("DJ Accept/Reject", test_dj_accept_reject_bookings),
        
        # === NEGATIVE TESTS ===
        ("NEGATIVO: QR Code Invalido", test_invalid_qr_code),
        ("NEGATIVO: Sessione Senza Cookie", test_validate_session_without_cookie),
        ("NEGATIVO: Cookie Session Invalido", test_validate_session_invalid_cookie),
        ("NEGATIVO: Booking Senza Sessione", test_user_booking_without_cookie),
        ("NEGATIVO: Canzone Inesistente", test_user_booking_nonexistent_song),
        ("NEGATIVO: Venue Inattivo", test_user_booking_venue_inactive),
        ("NEGATIVO: DJ Senza Auth", test_dj_unauthorized_access),
        ("NEGATIVO: DJ Venue Altrui", test_dj_access_wrong_venue),
        ("NEGATIVO: Sessione Scaduta", test_session_expiry_real),
        ("NEGATIVO: Cambio Venue Invalida Sessioni",test_venue_change_invalidates_session),
        
		("User Cancella Propria Prenotazione", test_user_can_delete_own_booking),
        ("User Cancella Prenotazioni altrui (NEGATIVO)", test_user_cannot_delete_others_booking),
		("NEGATIVO: Cancellazione Venue Inattivo", test_user_cannot_delete_with_venue_inactive),
		("NEGATIVO: Cancellazione ID Inesistente", test_user_delete_booking_invalid_id),
        
		# DJ Profile Management
		("DJ Get Profile Info", test_get_dj_profile_info),
		("NEGATIVO: DJ Get Profile Senza Auth", test_get_dj_profile_without_auth),
		("DJ Update Profile", test_update_dj_profile_success),
		("NEGATIVO: DJ Update Email Duplicata", test_update_dj_profile_duplicate_email),
		("DJ Change Password", test_change_password_success),
		("NEGATIVO: DJ Change Password Errata", test_change_password_wrong_current),
		("NEGATIVO: DJ Logout Senza Auth", test_logout_without_auth),
        ("Cambio Password e Login", test_change_password_and_login),
        
        # Cleanup
        #("Cleanup", test_cleanup),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    start_time = time.time()
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result is True:
                passed += 1
            elif result is None:
                skipped += 1
                print_warning(f"⊘ {name} - SKIPPED")
            else:
                failed += 1
        except Exception as e:
            print_error(f"Eccezione in '{name}': {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    elapsed = time.time() - start_time
    
    # Summary
    print(f"\n{Colors.PURPLE}{'='*70}")
    print(f"  📊 RISULTATI COMPLETE BOOKING TEST SUITE")
    print(f"{'='*70}{Colors.END}\n")
    
    total = passed + failed
    print(f"Totale test: {total}")
    print(f"{Colors.GREEN}✓ Passati: {passed}{Colors.END}")
    print(f"{Colors.RED}✗ Falliti: {failed}{Colors.END}")
    if skipped > 0:
        print(f"{Colors.YELLOW}⊘ Skipped: {skipped}{Colors.END}")
    
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\nSuccesso: {percentage:.1f}%")
    print(f"Tempo: {elapsed:.2f}s")
    
    if failed == 0 and passed > 0:
        print(f"\n{Colors.GREEN}🎉 TUTTI I TEST BOOKING PASSATI! 🎉{Colors.END}\n")
        print(f"{Colors.GREEN}✓ Prenotazioni DJ funzionano (session_id NULL){Colors.END}")
        print(f"{Colors.GREEN}✓ Prenotazioni User funzionano (session_id collegato){Colors.END}")
        print(f"{Colors.GREEN}✓ Isolamento utenti funziona{Colors.END}")
        print(f"{Colors.GREEN}✓ Rate limiting funziona (max 3 per session){Colors.END}")
        print(f"{Colors.GREEN}✓ DJ vede tutte le prenotazioni{Colors.END}")
        print(f"{Colors.GREEN}✓ Validazione errori funziona{Colors.END}")
        print(f"{Colors.GREEN}✓ Sicurezza endpoint protetta{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}⚠ ALCUNI TEST SONO FALLITI{Colors.END}\n")
        if failed > 0:
            print(f"{Colors.RED}Focus sui test falliti per debugging{Colors.END}")

if __name__ == "__main__":
    run_complete_booking_tests()