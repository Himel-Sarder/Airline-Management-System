import streamlit as st
import sqlite3
from sqlite3 import Error
import datetime

# Database Configuration
DATABASE = 'airline.db'

# Initialize Database Tables
def create_tables():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # Users Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT CHECK(role IN ('admin', 'passenger')) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Flights Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_number TEXT NOT NULL,
                departure_airport TEXT NOT NULL,
                arrival_airport TEXT NOT NULL,
                departure_time DATETIME NOT NULL,
                arrival_time DATETIME NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT DEFAULT 'Scheduled'
            )
        """)

        # Bookings Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                flight_id INTEGER,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                seat_number TEXT,
                status TEXT DEFAULT 'Confirmed',
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
                UNIQUE (flight_id, seat_number)
            )
        """)

        # Crew Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS crew (
                crew_id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_id INTEGER,
                crew_name TEXT NOT NULL,
                role TEXT NOT NULL,
                contact_info TEXT,
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
            )
        """)

        conn.commit()
    except Error as e:
        st.error(f"Error creating tables: {e}")
    finally:
        if conn:
            conn.close()

# Database Connection Helper
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Background Setting
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-31.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Database Operations
def add_user(username, password, email, role):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        """, (username, password, email, role))
        conn.commit()
        return c.lastrowid
    except Error as e:
        st.error(f"Error adding user: {e}")
        return None
    finally:
        conn.close()

def authenticate_user(username, password, role):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM users 
            WHERE username = ? AND password = ? AND role = ?
        """, (username, password, role))
        return c.fetchone()
    except Error as e:
        st.error(f"Error authenticating user: {e}")
        return None
    finally:
        conn.close()

# Updated Profile Section with Password Change
def show_passenger_profile():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-5.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", 
                       (st.session_state.user_id,)).fetchone()
    conn.close()

    st.subheader("Passenger Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
            <div style="background-color: #7f8c8d; padding: 20px; border-radius: 10px;">
                <h3 style="margin-bottom: 15px;">Account Overview</h3>
                <div style="margin-bottom: 10px;">
                    <label>Username</label>
                    <div>{user['username']}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <label>Member Since</label>
                    <div>{datetime.datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.expander("Personal Information", expanded=True):
            st.markdown(f"""
                <table style="width:100%">
                    <tr><td>Email Address</td><td>{user['email']}</td></tr>
                    <tr><td>Account Type</td><td>Passenger</td></tr>
                </table>
            """, unsafe_allow_html=True)
        
        with st.expander("Update Password"):
            with st.form("password_update_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new_password != confirm_password:
                        st.error("New passwords do not match")
                    else:
                        try:
                            conn = get_db()
                            db_password = conn.execute("SELECT password FROM users WHERE user_id = ?", 
                                                     (st.session_state.user_id,)).fetchone()['password']
                            
                            if current_password != db_password:
                                st.error("Current password is incorrect")
                            else:
                                conn.execute("UPDATE users SET password = ? WHERE user_id = ?",
                                           (new_password, st.session_state.user_id))
                                conn.commit()
                                st.success("Password updated successfully")
                        except Error as e:
                            st.error(f"Password update failed: {str(e)}")
                        finally:
                            conn.close()

def find_flights():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-18.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Find Flights")
    with st.form("flight_search"):
        dep_airport = st.text_input("Departure Airport")
        arr_airport = st.text_input("Arrival Airport")
        dep_date = st.date_input("Departure Date")

        if st.form_submit_button("Search"):
            conn = get_db()
            flights = conn.execute("""
                SELECT * FROM flights 
                WHERE departure_airport = ? 
                AND arrival_airport = ? 
                AND DATE(departure_time) = ?
            """, (dep_airport, arr_airport, dep_date)).fetchall()
            conn.close()

            if flights:
                st.subheader("Available Flights")
                for flight in flights:
                    booked = get_booked_seats(flight['flight_id'])
                    st.write(f"Flight {flight['flight_number']}")
                    st.write(f"Departure: {flight['departure_time']}")
                    st.write(f"Arrival: {flight['arrival_time']}")
                    st.write(f"Available Seats: {flight['capacity'] - booked}")
                    st.write("---")
            else:
                st.warning("No flights found matching your criteria.")

def get_booked_seats(flight_id):
    conn = get_db()
    count = conn.execute("""
        SELECT COUNT(*) FROM bookings 
        WHERE flight_id = ? AND status = 'Confirmed'
    """, (flight_id,)).fetchone()[0]
    conn.close()
    return count

def book_flight():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-18.jpg ");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Book a Flight")

    conn = get_db()
    all_flights = conn.execute("""
        SELECT flight_id, flight_number, departure_airport, arrival_airport, departure_time
        FROM flights
        ORDER BY departure_time
    """).fetchall()
    conn.close()

    if not all_flights:
        st.warning("No flights available. Please ask an admin to add flights first.")
        return

    flight_options = [
        f"{f['flight_id']} - {f['flight_number']} ({f['departure_airport']}→{f['arrival_airport']} @ {f['departure_time']})"
        for f in all_flights
    ]
    selected = st.selectbox("Select Flight to Book", flight_options)
    flight_id = int(selected.split(" - ")[0])

    num_seats = st.number_input("Number of Seats", min_value=1, max_value=10, value=1)

    conn = get_db()
    booked_seats = {row['seat_number'] for row in conn.execute("SELECT seat_number FROM bookings WHERE flight_id = ?", (flight_id,))}
    conn.close()

    seat_sections = {
        "Business Class (Rows 2-11)": {
            row: [f"{row}{seat}" for seat in ["A", "F"]]
            for row in range(2, 12)
        },
        "Economy Class (Rows 20-30)": {
            row: [f"{row}{seat}" for seat in ["A", "B", "C", "D", "E", "F"]]
            for row in range(20, 31)
        }
    }

    if 'selected_seats' not in st.session_state:
        st.session_state.selected_seats = []

    st.markdown("""
    <style>
    button[kind="secondary"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    
    button[kind="secondary"]:disabled {
        background-color: #ff4444 !important;
        color: white !important;
    }
    
    button[kind="primary"] {
        background-color: #FFEB3B !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    for section_name, rows in seat_sections.items():
        st.subheader(section_name)
        for row_label, seats in rows.items():
            cols = st.columns(len(seats))
            for idx, seat in enumerate(seats):
                with cols[idx]:
                    is_booked = seat in booked_seats
                    is_selected = seat in st.session_state.selected_seats
                    btn_type = "primary" if is_selected else "secondary"
                    
                    if st.button(
                        seat,
                        key=f"seat_{seat}",
                        disabled=is_booked,
                        help="Booked" if is_booked else "Click to select",
                        type=btn_type
                    ):
                        if seat in st.session_state.selected_seats:
                            st.session_state.selected_seats.remove(seat)
                        else:
                            if len(st.session_state.selected_seats) < num_seats:
                                st.session_state.selected_seats.append(seat)
                            else:
                                st.warning(f"You can select up to {num_seats} seats")
                        st.rerun()

    if st.session_state.selected_seats:
        st.write(f"Selected seats: {', '.join(st.session_state.selected_seats)}")

    if st.button("Confirm Booking") and 'user_id' in st.session_state:
        if len(st.session_state.selected_seats) != num_seats:
            st.error(f"Please select exactly {num_seats} seats")
            return

        try:
            conn = get_db()
            current_booked = {row['seat_number'] for row in conn.execute("SELECT seat_number FROM bookings WHERE flight_id = ?", (flight_id,))}
            
            conflicting = set(st.session_state.selected_seats) & current_booked
            if conflicting:
                st.error(f"Seat(s) {', '.join(conflicting)} were just booked by someone else")
                return

            for seat in st.session_state.selected_seats:
                conn.execute("""
                    INSERT INTO bookings (user_id, flight_id, seat_number)
                    VALUES (?, ?, ?)
                """, (st.session_state.user_id, flight_id, seat))
            conn.commit()
            st.success(f"Successfully booked {num_seats} seat(s)!")
            st.session_state.selected_seats = []
            st.rerun()
        except Error as e:
            conn.rollback()
            st.error(f"Booking failed: {e}")
        finally:
            conn.close()

# Admin Pages
def manage_flights():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-3.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Manage Flights")
    action = st.selectbox("Action", ["Add Flight", "Update Flight", "Delete Flight"])

    if action == "Add Flight":
        with st.form("add_flight"):
            flight_number = st.text_input("Flight Name")
            dep_airport = st.text_input("Departure Airport")
            arr_airport = st.text_input("Arrival Airport")

            col1, col2 = st.columns(2)
            with col1:
                dep_date = st.date_input("Departure Date")
                dep_time = st.time_input("Departure Time")
            with col2:
                arr_date = st.date_input("Arrival Date")
                arr_time = st.time_input("Arrival Time")

            departure_datetime = f"{dep_date} {dep_time}"
            arrival_datetime = f"{arr_date} {arr_time}"
            capacity = st.number_input("Capacity", min_value=1)

            if st.form_submit_button("Add Flight"):
                try:
                    conn = get_db()
                    conn.execute("""
                        INSERT INTO flights (
                            flight_number, departure_airport, arrival_airport,
                            departure_time, arrival_time, capacity
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (flight_number, dep_airport, arr_airport,
                          departure_datetime, arrival_datetime, capacity))
                    conn.commit()
                    st.success("Flight added successfully!")
                except Error as e:
                    st.error(f"Error adding flight: {e}")
                finally:
                    conn.close()

    elif action == "Update Flight":
        conn = get_db()
        flights = conn.execute("SELECT * FROM flights").fetchall()
        if flights:
            flight_choice = st.selectbox(
                "Select Flight",
                [f"{f['flight_id']} - {f['flight_number']}" for f in flights]
            )
            flight_id = int(flight_choice.split(" - ")[0])
            flight = conn.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,)).fetchone()

            with st.form("update_flight"):
                new_number = st.text_input("Flight Number", value=flight['flight_number'])
                new_dep = st.text_input("Departure Airport", value=flight['departure_airport'])
                new_arr = st.text_input("Arrival Airport", value=flight['arrival_airport'])

                current_dep = datetime.datetime.strptime(flight['departure_time'], '%Y-%m-%d %H:%M:%S')
                current_arr = datetime.datetime.strptime(flight['arrival_time'], '%Y-%m-%d %H:%M:%S')

                col1, col2 = st.columns(2)
                with col1:
                    new_dep_date = st.date_input("Departure Date", value=current_dep.date())
                    new_dep_time = st.time_input("Departure Time", value=current_dep.time())
                with col2:
                    new_arr_date = st.date_input("Arrival Date", value=current_arr.date())
                    new_arr_time = st.time_input("Arrival Time", value=current_arr.time())

                new_dep_datetime = f"{new_dep_date} {new_dep_time}"
                new_arr_datetime = f"{new_arr_date} {new_arr_time}"

                new_cap = st.number_input("Capacity", value=flight['capacity'], min_value=1)
                new_status = st.selectbox(
                    "Status",
                    ["Scheduled", "Delayed", "Cancelled"],
                    index=["Scheduled", "Delayed", "Cancelled"].index(flight['status'])
                )

                if st.form_submit_button("Update Flight"):
                    conn.execute("""
                        UPDATE flights SET
                            flight_number = ?,
                            departure_airport = ?,
                            arrival_airport = ?,
                            departure_time = ?,
                            arrival_time = ?,
                            capacity = ?,
                            status = ?
                        WHERE flight_id = ?
                    """, (new_number, new_dep, new_arr, new_dep_datetime,
                          new_arr_datetime, new_cap, new_status, flight_id))
                    conn.commit()
                    st.success("Flight updated successfully!")
        conn.close()

    elif action == "Delete Flight":
        conn = get_db()
        flights = conn.execute("SELECT * FROM flights").fetchall()
        if flights:
            flight_choice = st.selectbox(
                "Select Flight to Delete",
                [f"{f['flight_id']} - {f['flight_number']}" for f in flights]
            )
            flight_id = int(flight_choice.split(" - ")[0])

            with st.form("delete_flight"):
                st.warning("Are you sure you want to delete this flight?")
                if st.form_submit_button("Confirm Delete"):
                    conn.execute("DELETE FROM flights WHERE flight_id = ?", (flight_id,))
                    conn.commit()
                    st.success("Flight deleted successfully!")
        conn.close()

def flight_overview():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-3.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Flight Management")

    conn = get_db()
    flights = conn.execute("SELECT * FROM flights ORDER BY departure_time DESC").fetchall()

    if not flights:
        st.warning("No flights found in the system")
        return

    flight_options = [
        f"{f['flight_id']} - {f['flight_number']} ({f['departure_airport']} to {f['arrival_airport']})"
        for f in flights
    ]
    selected_flight = st.selectbox("Select Flight to View Details", flight_options)
    flight_id = int(selected_flight.split(" - ")[0])
    flight_details = conn.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,)).fetchone()

    st.subheader("Flight Details")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            **Flight Number:** {flight_details['flight_number']}  
            **Departure:** {flight_details['departure_airport']}  
            **Departure Time:** {flight_details['departure_time']}  
            **Status:** {flight_details['status']}
        """)
    with col2:
        st.markdown(f"""
            **Arrival:** {flight_details['arrival_airport']}  
            **Arrival Time:** {flight_details['arrival_time']}  
            **Capacity:** {flight_details['capacity']}  
            **Booked Seats:** {get_booked_seats(flight_id)}
        """)

    st.subheader("Assigned Crew Members")
    crew_members = conn.execute("SELECT crew_name, role, contact_info FROM crew WHERE flight_id = ?", (flight_id,)).fetchall()
    if crew_members:
        for member in crew_members:
            st.markdown(f"""
                **Name:** {member['crew_name']}  
                **Role:** {member['role']}  
                **Contact:** {member['contact_info']}
            """)
            st.write("---")
    else:
        st.info("No crew members assigned to this flight")
    conn.close()

def manage_crew():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wonderfulengineering.com/wp-content/uploads/2014/05/airplane-wallpaper-3.jpg");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Manage Crew Members")
    action = st.selectbox("Action", ["Add Crew", "Update Crew", "Delete Crew"])

    conn = get_db()
    flights = conn.execute("SELECT flight_id, flight_number, departure_time FROM flights").fetchall()

    if action == "Add Crew":
        with st.form("add_crew_form"):
            if flights:
                flight_choice = st.selectbox(
                    "Select Flight",
                    [f"{f['flight_id']} - {f['flight_number']} ({f['departure_time'].split()[0]})" for f in flights]
                )
                flight_id = int(flight_choice.split(" - ")[0])
                crew_name = st.text_input("Crew Member Name")
                role = st.selectbox("Role", ["Pilot", "Co-Pilot", "Flight Attendant", "Engineer", "Catering Manager", "Hostess"])
                contact = st.text_input("Contact Information")

                if st.form_submit_button("Add Crew Member"):
                    conn.execute("""
                        INSERT INTO crew (flight_id, crew_name, role, contact_info)
                        VALUES (?, ?, ?, ?)
                    """, (flight_id, crew_name, role, contact))
                    conn.commit()
                    st.success("Crew member added successfully!")
            else:
                st.warning("No flights available. Please add flights first.")
    elif action == "Update Crew":
        crew_members = conn.execute("SELECT c.*, f.flight_number FROM crew c JOIN flights f ON c.flight_id = f.flight_id").fetchall()
        if crew_members:
            crew_choice = st.selectbox(
                "Select Crew Member to Update",
                [f"{c['crew_name']} - {c['role']} (Flight {c['flight_number']})" for c in crew_members]
            )
            selected_index = [f"{c['crew_name']} - {c['role']} (Flight {c['flight_number']})" for c in crew_members].index(crew_choice)
            selected_crew = crew_members[selected_index]

            with st.form("update_crew_form"):
                new_flight_choice = st.selectbox(
                    "Select New Flight",
                    [f"{f['flight_id']} - {f['flight_number']} ({f['departure_time'].split()[0]})" for f in flights],
                    index=[f['flight_id'] for f in flights].index(selected_crew['flight_id'])
                )
                new_flight_id = int(new_flight_choice.split(" - ")[0])
                new_name = st.text_input("Name", value=selected_crew['crew_name'])
                new_role = st.selectbox(
                    "Role",
                    ["Pilot", "Co-Pilot", "Flight Attendant", "Engineer", "Catering Manager", "Hostess"],
                    index=["Pilot", "Co-Pilot", "Flight Attendant", "Engineer", "Catering Manager", "Hostess"].index(selected_crew['role'])
                )
                new_contact = st.text_input("Contact Info", value=selected_crew['contact_info'])

                if st.form_submit_button("Update Crew Member"):
                    conn.execute("""
                        UPDATE crew SET
                            flight_id = ?,
                            crew_name = ?,
                            role = ?,
                            contact_info = ?
                        WHERE crew_id = ?
                    """, (new_flight_id, new_name, new_role, new_contact, selected_crew['crew_id']))
                    conn.commit()
                    st.success("Crew member updated successfully!")
        else:
            st.warning("No crew members found")
    elif action == "Delete Crew":
        crew_members = conn.execute("SELECT c.*, f.flight_number FROM crew c JOIN flights f ON c.flight_id = f.flight_id").fetchall()
        if crew_members:
            crew_choice = st.selectbox(
                "Select Crew Member to Delete",
                [f"{c['crew_name']} - {c['role']} (Flight {c['flight_number']})" for c in crew_members]
            )
            selected_index = [f"{c['crew_name']} - {c['role']} (Flight {c['flight_number']})" for c in crew_members].index(crew_choice)
            selected_crew = crew_members[selected_index]

            with st.form("delete_crew_form"):
                st.warning(f"Are you sure you want to delete {selected_crew['crew_name']}?")
                if st.form_submit_button("Confirm Delete"):
                    conn.execute("DELETE FROM crew WHERE crew_id = ?", (selected_crew['crew_id'],))
                    conn.commit()
                    st.success("Crew member deleted successfully!")
        else:
            st.warning("No crew members found")

    st.subheader("Current Crew Assignments")
    current_crew = conn.execute("""
        SELECT f.flight_number, c.crew_name, c.role, c.contact_info 
        FROM crew c 
        JOIN flights f ON c.flight_id = f.flight_id
        ORDER BY f.departure_time
    """).fetchall()
    if current_crew:
        for crew in current_crew:
            st.write(f"**Flight {crew['flight_number']}**")
            st.write(f"Name: {crew['crew_name']}")
            st.write(f"Role: {crew['role']}")
            st.write(f"Contact: {crew['contact_info']}")
            st.write("---")
    else:
        st.info("No crew members assigned to any flights")
    conn.close()

def main():
    set_background()
    create_tables()

    st.markdown("""
        <style>
        div[data-testid="column"] {
            flex: 1;
            min-width: 120px;
        }
        
        button[kind="primary"], button[kind="secondary"] {
            width: 100% !important;
            font-size: 14px !important;
            padding: 10px 15px !important;
            border: none !important;
            border-radius: 5px !important;
            transition: all 0.3s ease !important;
            color: #000000 !important;
            white-space: nowrap;
        }

        button[kind="primary"] {
            background-color: #FFD700 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        button[kind="secondary"] {
            background-color: #4CAF50 !important;
            color: #FFFFFF !important;
        }

        button[kind="secondary"]:hover {
            background-color: #45a049 !important;
            transform: translateY(-1px);
        }
        
        .stButton > button {
            width: 100% !important;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state.update({
            'logged_in': False,
            'role': None,
            'user_id': None,
            'menu': None
        })

    if not st.session_state.logged_in:
        st.markdown('<h1 style="color: white;">Airline Management System</h1>', unsafe_allow_html=True)
        user_type = st.radio("Select User Type", ["Passenger", "Admin"], horizontal=True)

        if user_type == "Passenger":
            action = st.radio("Choose Action", ["Login", "Register"], horizontal=True, key='passenger_action')
            if action == "Login":
                with st.form("passenger_login"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        user = authenticate_user(username, password, "passenger")
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.role = "passenger"
                            st.session_state.user_id = user['user_id']
                            st.session_state.menu = "Profile"
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
            elif action == "Register":
                with st.form("passenger_register"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    email = st.text_input("Email")
                    if st.form_submit_button("Register"):
                        if add_user(username, password, email, "passenger"):
                            st.success("Registration successful! Please login.")
        else:
            with st.form("admin_login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    user = authenticate_user(username, password, "admin")
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.session_state.user_id = user['user_id']
                        st.session_state.menu = "Flight Overview"
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
    else:
        st.markdown(f"<h2 style='text-align: center; color: white;'>{st.session_state.role.capitalize()} Dashboard</h2>", 
                    unsafe_allow_html=True)
        
        if st.session_state.role == "passenger":
            menu_options = ["Profile", "Find Flights", "Book Flight", "My Bookings", "Logout"]
        else:
            menu_options = ["Flight Overview", "Manage Flights", "Manage Crew", "Manage Bookings", "Logout"]
        
        cols = st.columns(len(menu_options))
        for i, option in enumerate(menu_options):
            with cols[i]:
                is_active = option == st.session_state.get('menu')
                button_type = "primary" if is_active else "secondary"
                if st.button(
                    f"**{option}**" if is_active else option,
                    key=f"nav_{option}",
                    type=button_type,
                    use_container_width=True
                ):
                    if option == "Logout":
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.session_state.menu = option
                        st.rerun()

        if st.session_state.role == "passenger":
            if st.session_state.menu == "Profile":
                show_passenger_profile()
            elif st.session_state.menu == "Find Flights":
                find_flights()
            elif st.session_state.menu == "Book Flight":
                book_flight()
            elif st.session_state.menu == "My Bookings":
                conn = get_db()
                bookings = conn.execute("""
                    SELECT b.booking_id, f.flight_number, f.departure_airport, f.arrival_airport, 
                           f.departure_time, b.seat_number, b.booking_date
                    FROM bookings b
                    JOIN flights f ON b.flight_id = f.flight_id
                    WHERE b.user_id = ?
                    ORDER BY b.booking_date DESC
                """, (st.session_state.user_id,)).fetchall()
                conn.close()

                st.subheader("My Bookings")
                if bookings:
                    for bk in bookings:
                        st.markdown(f"""
                            **Booking ID:** {bk['booking_id']}  
                            **Flight:** {bk['flight_number']} ({bk['departure_airport']}→{bk['arrival_airport']})  
                            **Departure Time:** {bk['departure_time']}  
                            **Seat:** {bk['seat_number']}  
                            **Booked At:** {bk['booking_date']}  
                        """)
                        st.write("---")
                else:
                    st.info("You have no bookings.")

        elif st.session_state.role == "admin":
            if st.session_state.menu == "Flight Overview":
                flight_overview()
            elif st.session_state.menu == "Manage Flights":
                manage_flights()
            elif st.session_state.menu == "Manage Crew":
                manage_crew()
            elif st.session_state.menu == "Manage Bookings":
                conn = get_db()
                all_bookings = conn.execute("""
                    SELECT b.booking_id, u.username, f.flight_number, f.departure_airport, 
                        f.arrival_airport, f.departure_time, b.seat_number, b.status, b.booking_date
                    FROM bookings b
                    JOIN users u ON b.user_id = u.user_id
                    JOIN flights f ON b.flight_id = f.flight_id
                    ORDER BY b.booking_date DESC
                """).fetchall()
                conn.close()

                st.subheader("All Bookings")
                if all_bookings:
                    for bk in all_bookings:
                        col1, col2 = st.columns([4,1])
                        with col1:
                            st.markdown(f"""
                                **Booking ID:** {bk['booking_id']}  
                                **User:** {bk['username']}  
                                **Flight:** {bk['flight_number']} ({bk['departure_airport']}→{bk['arrival_airport']})  
                                **Departure:** {bk['departure_time']}  
                                **Seat:** {bk['seat_number']}  
                                **Status:** {bk['status']}  
                                **Booked At:** {bk['booking_date']}  
                            """)
                        with col2:
                            with st.form(f"delete_booking_{bk['booking_id']}"):
                                if st.form_submit_button("🗑️ Delete"):
                                    try:
                                        conn = get_db()
                                        conn.execute("DELETE FROM bookings WHERE booking_id = ?", (bk['booking_id'],))
                                        conn.commit()
                                        st.success(f"Booking {bk['booking_id']} deleted successfully!")
                                        st.rerun()
                                    except Error as e:
                                        st.error(f"Error deleting booking: {e}")
                                    finally:
                                        conn.close()
                        st.write("---")
                else:
                    st.info("No bookings found.")

    st.markdown(
        """
        <hr style="margin-top: 50px;"/>
        <div style="text-align: center; padding: 10px;">
            <small>
                © 2025 <a href="https://www.linkedin.com/in/himel-sarder/" target="_blank">Himel Sarder</a> • All Rights Reserved <br/>
            </small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()