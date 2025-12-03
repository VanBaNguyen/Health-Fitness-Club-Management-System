# Health and Fitness Club Management System

**COMP 3005 - Fall 2025**
**Instructor:** Abdelghny Orogat
**Group Members:** Van Nguyen (101331941) and Siddig Ahmed (101332539)

## Video Demonstration
[Link to Video Demonstration](https://youtu.be/XoULYgeu4GI)

## Project Description
This project is a comprehensive Health and Fitness Club Management System designed to manage the daily operations of a fitness center. It supports three distinct user roles: **Members**, **Trainers**, and **Administrative Staff**. The system handles member registrations, profile management, class scheduling, room bookings, trainer availability, and billing/payment simulations.

The application is built using Python and relies on **SQLAlchemy** as an Object-Relational Mapper (ORM) to interact with a SQLite relational database (`health_club.db`). 

## How to Run the Project

### Prerequisites
- Python 3.x installed

### Installation
1. Clone the repository or extract the project files.
2. Navigate to the project root directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution
Run the main application script from the root directory:
```bash
python app/app.py
```
Follow the on-screen CLI prompts to navigate between user roles (Admin, Trainer, Member) and perform operations.

## Project Structure
```
/project-root
  ├── app/
  │   └── app.py            # Main application entry point and CLI interface
  ├── models/               # SQLAlchemy ORM Entity Classes
  │   ├── user.py           # Base User class
  │   ├── member.py         # Member entity logic
  │   ├── trainer.py        # Trainer entity logic
  │   ├── admin.py          # Admin entity logic
  │   ├── room.py           # Room management
  │   ├── fitness_class.py  # Class scheduling
  │   ├── enrollment.py     # Class enrollments
  │   ├── billing.py        # Billing and payments
  │   └── ...
  ├── docs/                 # Documents
  │   └── ERD.pdf           # ER Diagram and schema
  ├── health_club.db        # SQLite database (generated on first run)
  └── requirements.txt      # Python dependencies
```

## Database Design

### ER Model
The ER model defines the entities (Member, Trainer, Room, Class, Bill, etc.) and their relationships. See `docs/ERD.pdf` for the visual representation.

### Entity Classifications

- **Trainer**: Regular Entity (Has its own Primary Key `id`)
- **Member**: Regular Entity (Has its own Primary Key `id`)
- **Rooms**: Regular Entity (Has its own Primary Key `id`)
- **Classes**: Regular Entity (Has its own Primary Key `id`)
- **Bills**: Regular Entity (Has its own Primary Key `id`)
- **Payments**: Regular Entity (Has its own Primary Key `id`)
- **Bill Line Items**: Regular Entity (Has its own Primary Key `id`, although conceptually it is often a weak entity, the schema implements it with a surrogate key)
- **Trainer Availability**: Regular Entity (Has its own Primary Key `id`)
- **Enrollments**: Weak Entity (Does not have its own surrogate Primary Key; its Primary Key is a composite of Foreign Keys `class_id` and `member_id`)

### Entity Attribute Details

#### Member (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **name**: Simple, Single-valued
- **email**: Simple, Single-valued
- **age**: Simple, Single-valued
- **gender**: Simple, Single-valued
- **weight_goal**: Simple, Single-valued
- **current_weight**: Simple, Single-valued

#### Trainer (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **name**: Simple, Single-valued
- **email**: Simple, Single-valued

#### Room (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **name**: Simple, Single-valued
- **capacity**: Simple, Single-valued

#### Class (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **name**: Simple, Single-valued
- **day_of_week**: Simple, Single-valued
- **start_time**: Simple, Single-valued
- **end_time**: Simple, Single-valued
- **capacity**: Simple, Single-valued
- **trainer_id**: Simple, Single-valued [Foreign Key]
- **room_id**: Simple, Single-valued [Foreign Key]

#### TrainerAvailability (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **day_of_week**: Simple, Single-valued
- **start_time**: Simple, Single-valued
- **end_time**: Simple, Single-valued
- **trainer_id**: Simple, Single-valued [Foreign Key]

#### Bill (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **status**: Simple, Single-valued
- **created_at**: Simple, Single-valued
- **member_id**: Simple, Single-valued [Foreign Key]

#### BillLineItem (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **description**: Simple, Single-valued
- **amount**: Simple, Single-valued
- **bill_id**: Simple, Single-valued [Foreign Key]

#### Payment (Regular Entity)
- **id**: Simple, Single-valued [Primary Key]
- **amount**: Simple, Single-valued
- **created_at**: Simple, Single-valued
- **status**: Simple, Single-valued
- **transaction_code**: Simple, Single-valued
- **bill_id**: Simple, Single-valued [Foreign Key]

#### Enrollment (Weak Entity)
- **member_id**: Simple, Single-valued [Primary Key (Composite), Foreign Key]
- **class_id**: Simple, Single-valued [Primary Key (Composite), Foreign Key]
- **registration_date**: Simple, Single-valued

## ORM Mapping (bonus)
We used SQLAlchemy to translate our ER diagram into code. The entities (like Member, Trainer, and Room) are defined as Python classes in the `models/` folder, inheriting from a shared `Base` class. We mapped attributes directly to database columns using `Column()` and handled relationships with `ForeignKey()` for the database constraints and `relationship()` for easy object navigation in Python.

For the user hierarchy, we went with Single Table Inheritance. The base `User` class handles the shared logic, while `Member` and `Trainer` subclasses handle specific roles, all stored within the `users` table using a `user_type` discriminator.

## Required Application Operations

### Member Functions
- **User Registration:** Create a new member profile.
- **Profile Management:** Update personal details, weight goals, and health metrics.
- **Dashboard:** View personal stats and enrolled classes.
- **Group Class Registration:** Browse and register for available classes (subject to capacity).

### Trainer Functions
- **Set Availability:** Define available working hours.
- **View Schedule:** See assigned classes and sessions.
- **Member Lookup:** Search for members by name to view their public profile and goals.

### Administrative Staff Functions
- **Room Management:** Create rooms and view room details.
- **Class Management:** Schedule classes, assign trainers and rooms, and update class details.
- **Billing & Payments:**
    - Generate bills for members.
    - Add line items (charges) to bills.
    - Record payments and update balance due.
    - View billing history.

## Assumptions

The program is a text-based interface simulates the user experience for all roles within a single executable for convenience. 

We're assuming that "admins" will all have the same abilities and not necessarily be different people such that they all need individual ids/names. Our interpretation of the admin role is that all admins will use 1 "admin panel" interface for their role, while trainers and members are individually treated.

It'd also likely be best if members were created, then trainers, then admin functionalities are run, in that order for the easiest way of viewing all the functionality of the program properly.
