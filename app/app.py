import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models')))

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time
from admin import Admin
from member import Member
from room import Room
from fitness_class import FitnessClass
from billing import Bill, BillLineItem, Payment
from user import Base
from trainer import Trainer



# 1 = admin
# 2 = trainer
# 3 = member

# Database setup
engine = create_engine("sqlite:///health_club.db", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    """Get a database session."""
    return Session()

def get_day_name(day_num: int) -> str:
    days = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return days.get(day_num, f"Day {day_num}")

def prompt_time(label: str) -> time:
    while True:
        raw = input(f"{label} (HH:MM): ").strip()
        try:
            dt = datetime.strptime(raw, "%H:%M")
            return dt.time()
        except ValueError:
            print("Invalid time format. Use HH:MM.")

def prompt_day(label: str) -> int:
    print("\nDays of the week:")
    print("  1: Monday")
    print("  2: Tuesday")
    print("  3: Wednesday")
    print("  4: Thursday")
    print("  5: Friday")
    print("  6: Saturday")
    print("  7: Sunday")
    while True:
        try:
            day = int(input(f"{label} (1-7): ").strip())
            if 1 <= day <= 7:
                return day
            print("Day must be between 1 and 7.")
        except ValueError:
            print("Invalid input. Enter a number.")

def admin_menu():
    db = get_db()

    while True:
        try:
            prompt = (
                "\n=== Admin Menu ===\n"
                "\t0 - Exit\n"
                "\n\t-- Room Management --\n"
                "\t1 - Create Room\n"
                "\t2 - List Rooms\n"
                "\n\t-- Class Management --\n"
                "\t3 - Schedule Fitness Class\n"
                "\t4 - Update Fitness Class\n"
                "\t5 - List Fitness Classes\n"
                "\n\t-- Billing & Payments --\n"
                "\t6 - Generate Bill for Member\n"
                "\t7 - Add Bill Line Item\n"
                "\t8 - Record Payment\n"
                "\t9 - View Bills\n"
                "\t13 - Delete Bill\n"
                "\n\t-- User/Staff Management --\n"
                "\t10 - View Members\n"
                "\t11 - View Trainers\n"
                "\t12 - View Trainer Availability\n"
                "Enter choice: "
            )
            choice = int(input(prompt))
            if choice not in range(0, 14):
                raise ValueError
        except (ValueError, EOFError):
            print("Invalid input, try again.")
            continue

        if choice == 0:
            print("Exiting admin menu...")
            db.close()
            break

        elif choice == 1:
            try:
                name = input("Enter room name: ").strip()
                if not name:
                    raise ValueError("Room name cannot be empty.")
                capacity_input = input("Enter capacity (optional): ").strip()
                capacity = int(capacity_input) if capacity_input else None
                room = Admin.create_room(db=db, name=name, capacity=capacity)
                print(f"\nRoom created. ID: {room.id}, Name: {room.name}")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 2:
            rooms = db.query(Room).order_by(Room.id).all()
            if not rooms:
                print("\nNo rooms found.")
            else:
                print("\nRooms:")
                for room in rooms:
                    capacity = room.capacity if room.capacity is not None else "N/A"
                    print(f"  ID {room.id}: {room.name} (Capacity: {capacity})")

        elif choice == 3:
            try:
                name = input("Class name: ").strip()
                if not name:
                    raise ValueError("Class name cannot be empty.")
                trainer_id = int(input("Trainer ID: ").strip())
                trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
                if trainer is None:
                    raise ValueError("Trainer not found.")
                
                day_of_week = prompt_day("Day of week")
                start_time = prompt_time("Start time")
                end_time = prompt_time("End time")
                
                room_id_input = input("Room ID (optional): ").strip()
                room_id = int(room_id_input) if room_id_input else None
                room = None
                if room_id is not None:
                    room = db.query(Room).filter(Room.id == room_id).first()
                    if room is None:
                        raise ValueError("Room not found.")
                
                capacity_input = input("Capacity (optional): ").strip()
                capacity = int(capacity_input) if capacity_input else None
                
                if room:
                    if capacity is None:
                        capacity = room.capacity
                    elif room.capacity is not None and capacity > room.capacity:
                        raise ValueError(f"Capacity cannot exceed room capacity ({room.capacity}).")

                fitness_class = FitnessClass.schedule(
                    db=db,
                    name=name,
                    trainer_id=trainer_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    room_id=room_id,
                    capacity=capacity,
                )
                print(f"\nClass scheduled. ID: {fitness_class.id}")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 4:
            try:
                class_id = int(input("Class ID to update: ").strip())
                print("Press Enter to keep existing values.")
                name = input("New class name: ").strip() or None
                trainer_input = input("New trainer ID: ").strip()
                trainer_id = int(trainer_input) if trainer_input else None
                if trainer_id is not None:
                    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
                    if trainer is None:
                        raise ValueError("Trainer not found.")
                room_input = input("New room ID: ").strip()
                room_id = int(room_input) if room_input else None
                if room_id is not None:
                    room = db.query(Room).filter(Room.id == room_id).first()
                    if room is None:
                        raise ValueError("Room not found.")
                
                day_input = input("New day (1-7) (optional): ").strip()
                day_of_week = int(day_input) if day_input else None
                
                start_input = input("New start time (HH:MM) (optional): ").strip()
                start_time = (
                    datetime.strptime(start_input, "%H:%M").time() if start_input else None
                )
                end_input = input("New end time (HH:MM) (optional): ").strip()
                end_time = (
                    datetime.strptime(end_input, "%H:%M").time() if end_input else None
                )
                
                capacity_input = input("New capacity: ").strip()
                capacity = int(capacity_input) if capacity_input else None
                updated = FitnessClass.update_schedule(
                    db=db,
                    class_id=class_id,
                    name=name,
                    trainer_id=trainer_id,
                    room_id=room_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    capacity=capacity,
                )
                print(f"\nClass updated. ID: {updated.id}")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 5:
            classes = db.query(FitnessClass).order_by(FitnessClass.day_of_week, FitnessClass.start_time).all()
            if not classes:
                print("\nNo classes scheduled.")
            else:
                print("\nScheduled Classes:")
                for cls in classes:
                    print(
                        f"  ID {cls.id}: {cls.name} | Trainer {cls.trainer_id} | "
                        f"{get_day_name(cls.day_of_week)} {cls.start_time} - {cls.end_time} | Room {cls.room_id or 'N/A'} | "
                        f"Capacity {cls.capacity or 'N/A'}"
                    )

        elif choice == 6:
            try:
                member_id = int(input("Member ID: ").strip())
                member = db.query(Member).filter(Member.id == member_id).first()
                if member is None:
                    raise ValueError("Member not found.")
                bill = Bill.create(db=db, member_id=member_id)
                print(f"\nBill created. ID: {bill.id} for {member.name}")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 7:
            try:
                bill_id = int(input("Bill ID: ").strip())
                bill = db.query(Bill).filter(Bill.id == bill_id).first()
                if bill is None:
                    raise ValueError("Bill not found.")
                description = input("Line item description: ").strip()
                if not description:
                    raise ValueError("Description cannot be empty.")
                amount = float(input("Amount: ").strip())
                item = BillLineItem(bill_id=bill.id, description=description, amount=amount)
                db.add(item)
                db.commit()
                db.refresh(item)
                # Refresh bill to get updated computed properties
                db.refresh(bill)
                bill.update_status(db)
                print(
                    f"\nLine item added. Total: {bill.total_amount:.2f}, "
                    f"Due: {bill.amount_due:.2f}"
                )
            except ValueError as e:
                db.rollback()
                print(f"\nError: {e}")
            except Exception as e:
                db.rollback()
                print(f"\nUnexpected error: {e}")

        elif choice == 8:
            try:
                bill_id = int(input("Bill ID: ").strip())
                bill = db.query(Bill).filter(Bill.id == bill_id).first()
                if bill is None:
                    raise ValueError("Bill not found.")
                
                print(f"Amount due: {bill.amount_due:.2f}")
                amount_input = input("Payment amount: ").strip()
                amount = float(amount_input)
                
                payment = Payment.record(db=db, bill=bill, amount=amount)
                print(
                    f"\nPayment recorded. Amount: {payment.amount:.2f}, "
                    f"New amount due: {bill.amount_due:.2f}"
                )
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 9:
            try:
                member_input = input("Member ID (press Enter for all): ").strip()
                query = db.query(Bill)
                if member_input:
                    member_id = int(member_input)
                    query = query.filter(Bill.member_id == member_id)
                bills = query.order_by(Bill.created_at.desc()).all()
                if not bills:
                    print("\nNo bills found.")
                    continue
                for bill in bills:
                    print(
                        f"\nBill {bill.id} | Member {bill.member_id} | "
                        f"Total {bill.total_amount:.2f} | Paid {bill.amount_paid:.2f} | "
                        f"Due {bill.amount_due:.2f} | Status {bill.status}"
                    )
                    if bill.line_items:
                        print("  Line Items:")
                        for item in bill.line_items:
                            print(f"    - {item.description}: {item.amount:.2f}")
                    if bill.payments:
                        print("  Payments:")
                        for payment in bill.payments:
                            print(
                                f"    - {payment.created_at.strftime('%Y-%m-%d %H:%M')}: ${payment.amount:.2f}"
                            )
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 10:
            members = db.query(Member).order_by(Member.id).all()
            if not members:
                print("\nNo members found.")
            else:
                print("\nMembers:")
                for member in members:
                    age = member.age if member.age is not None else "N/A"
                    gender = member.gender or "N/A"
                    current_weight = f"{member.current_weight} kg" if member.current_weight else "N/A"
                    weight_goal = f"{member.weight_goal} kg" if member.weight_goal else "N/A"
                    print(
                        f"  ID {member.id}: {member.name or 'Unnamed'} | "
                        f"{member.email or 'No Email'} | Age: {age} | Gender: {gender} | "
                        f"Weight: {current_weight} | Goal: {weight_goal}"
                    )

        elif choice == 11:
            trainers = db.query(Trainer).order_by(Trainer.id).all()
            if not trainers:
                print("\nNo trainers found.")
            else:
                print("\nTrainers:")
                for trainer in trainers:
                    print(
                        f"  ID {trainer.id}: {trainer.name or 'Unnamed'} | "
                        f"{trainer.email or 'No Email'}"
                    )

        elif choice == 12:
            availabilities = Admin.get_all_trainer_availabilities(db=db)
            if not availabilities:
                print("\nNo trainer availability found.")
            else:
                print("\nTrainer Availability:")
                for avail in availabilities:
                    print(
                        f"  Trainer: {avail.trainer.name} | {get_day_name(avail.day_of_week)}: {avail.start_time} - {avail.end_time}"
                    )

        elif choice == 13:
            try:
                bill_id = int(input("Bill ID to delete: ").strip())
                bill = db.query(Bill).filter(Bill.id == bill_id).first()
                if bill is None:
                    raise ValueError("Bill not found.")
                
                db.delete(bill)
                db.commit()
                print(f"\nBill {bill_id} deleted successfully.")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                db.rollback()
                print(f"\nUnexpected error: {e}")

def member_menu():
    db = get_db()
    
    while True:
        try:
            prompt = (
                "\n=== Member Menu ===\n"
                "\t0 - Exit\n"
                "\t1 - Register (Create new member)\n"
                "\t2 - Login\n"
                "Enter choice: "
            )

            choice = int(input(prompt))
            if choice not in range(0, 3):
                raise ValueError
            
        except (ValueError, EOFError):
            print("Invalid input, try again.")
            continue
            
        if choice == 0:
            print("Exiting...")
            db.close()
            break

        elif choice == 1:
            # Register new member
            try:
                print("\n=== Member Registration ===")
                name = input("Enter your name: ").strip()
                email = input("Enter your email: ").strip()
                age_input = input("Enter your age (optional, press Enter to skip): ").strip()
                age = int(age_input) if age_input else None
                gender = input("Enter your gender (optional, press Enter to skip): ").strip() or None
                current_weight_input = input("Enter your current weight in kg (optional, press Enter to skip): ").strip()
                current_weight = float(current_weight_input) if current_weight_input else None
                weight_goal_input = input("Enter your weight goal in kg (optional, press Enter to skip): ").strip()
                weight_goal = float(weight_goal_input) if weight_goal_input else None
                
                new_member = Member.create(
                    db=db,
                    name=name,
                    email=email,
                    age=age,
                    gender=gender,
                    current_weight=current_weight,
                    weight_goal=weight_goal,
                )
                print(f"\nMember registered successfully! ID: {new_member.id}, Email: {new_member.email}")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 2:
            # Login
            try:
                print("\n=== Member Login ===")
                email = input("Enter your email: ").strip()
                
                member = db.query(Member).filter(Member.email == email).first()
                
                if member is None:
                    print("\nInvalid email.")
                    continue
                
                print(f"\nWelcome, {member.name}!")
                logged_in_member_menu(db, member)
                
            except Exception as e:
                print(f"\n✗ Error: {e}")

def logged_in_member_menu(db, member: Member):
    while True:
        try:
            prompt = (
                f"\n=== Member Dashboard - {member.name} ===\n"
                "\t0 - Logout\n"
                "\t1 - View Dashboard\n"
                "\t2 - Update Profile\n"
                "\t3 - Register for Group Class\n"
                "Enter choice: "
            )

            choice = int(input(prompt))
            if choice not in range(0, 4):
                raise ValueError
            
        except (ValueError, EOFError):
            print("Invalid input, try again.")
            continue
            
        if choice == 0:
            print(f"\nLogged out. Goodbye, {member.name}!")
            break

        elif choice == 1:
            try:
                print("\n=== Dashboard ===")
                dashboard = member.get_dashboard(db)
                
                print(f"\nProfile:")
                print(f"  Name: {dashboard['name']}")
                print(f"  Email: {dashboard['email']}")
                print(f"  Age: {dashboard['age'] if dashboard['age'] else 'N/A'}")
                print(f"  Gender: {dashboard['gender'] if dashboard['gender'] else 'N/A'}")
                print(f"  Current Weight: {dashboard['current_weight']} kg" if dashboard['current_weight'] else "  Current Weight: N/A")
                print(f"  Weight Goal: {dashboard['weight_goal']} kg" if dashboard['weight_goal'] else "  Weight Goal: N/A")
                
                print(f"\nEnrolled Classes ({len(dashboard['enrolled_classes'])}):")  
                if dashboard["enrolled_classes"]:
                    for session in dashboard["enrolled_classes"]:
                        print(f"  Class ID: {session['session_id']} | {session['name']}")
                        print(f"    {get_day_name(session['day_of_week'])} | {session['start_time']} - {session['end_time']}")
                else:
                    print("  No enrolled classes")
                    
            except Exception as e:
                print(f"\nError: {e}")

        elif choice == 2:
            try:
                print("\n=== Update Profile ===")
                print("(Press Enter to skip updating a field)")
                name = input(f"Name (current: {member.name}): ").strip() or None
                age_input = input(f"Age (current: {member.age}): ").strip()
                age = int(age_input) if age_input else None
                gender = input(f"Gender (current: {member.gender}): ").strip() or None
                current_weight_input = input(f"Current Weight in kg (current: {member.current_weight}): ").strip()
                current_weight = float(current_weight_input) if current_weight_input else None
                weight_goal_input = input(f"Weight Goal in kg (current: {member.weight_goal}): ").strip()
                weight_goal = float(weight_goal_input) if weight_goal_input else None
                
                member.update_profile(db=db, name=name, age=age, gender=gender, current_weight=current_weight, weight_goal=weight_goal)
                print("\nProfile updated successfully!")
                
            except ValueError as e:
                print(f"\nInvalid input: {e}")
            except Exception as e:
                print(f"\nError: {e}")

        elif choice == 3:
            try:
                print("\n=== Register for Group Class ===")
                
                # Show available group classes
                available_classes = (
                    db.query(FitnessClass)
                    .order_by(FitnessClass.day_of_week, FitnessClass.start_time)
                    .all()
                )
                
                if not available_classes:
                    print("No available group classes found.")
                    continue
                
                print("\nAvailable Group Classes:")
                for cls in available_classes:
                    print(f"  Class ID: {cls.id} | {cls.name}")
                    print(f"    {get_day_name(cls.day_of_week)} | {cls.start_time} - {cls.end_time}")
                
                class_id = int(input("\nEnter class ID to register: ").strip())
                
                enrollment = member.register_for_class(db=db, class_id=class_id)
                print(f"\nRegistered for group class successfully! Enrollment date: {enrollment.registration_date}")
                
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nError: {e}")

def trainer_menu():
    db = get_db()

    while True:
        try:
            prompt = (
                "\n=== Trainer Menu ===\n"
                "\t0 - Exit\n"
                "\t1 - Register (Create new trainer)\n"
                "\t2 - Login\n"
                "Enter choice: "
            )
            choice = int(input(prompt))
            if choice not in range(0, 3):
                raise ValueError
        except (ValueError, EOFError):
            print("Invalid input, try again.")
            continue

        if choice == 0:
            print("Exiting trainer menu...")
            db.close()
            break

        elif choice == 1:
            try:
                print("\n=== Register Trainer ===")
                name = input("Enter your name: ").strip()
                email = input("Enter your email: ").strip()
                trainer = Trainer.create(db=db, name=name, email=email)
                print(f"\nTrainer account created. ID: {trainer.id}, Email: {trainer.email}")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 2:
            try:
                print("\n=== Trainer Login ===")
                email = input("Enter your email: ").strip()

                trainer = (
                    db.query(Trainer)
                    .filter(
                        Trainer.email == email,
                    )
                    .first()
                )

                if trainer is None:
                    print("\nInvalid email.")
                    continue

                print(f"\nWelcome, {trainer.name}!")
                logged_in_trainer_menu(db, trainer)
            except Exception as e:
                print(f"\n✗ Error: {e}")


def logged_in_trainer_menu(db, trainer: Trainer):
    """Menu for logged-in trainer operations."""

    while True:
        try:
            prompt = (
                f"\n=== Trainer Dashboard - {trainer.name} ===\n"
                "\t0 - Logout\n"
                "\n\t-- Schedule --\n"
                "\t1 - View Schedule\n"
                "\n\t-- Availability --\n"
                "\t2 - Set Availability\n"
                "\t4 - View Availability\n"
                "\n\t-- Members --\n"
                "\t3 - Lookup Member\n"
                "Enter choice: "
            )
            choice = int(input(prompt))
            if choice not in range(0, 5):
                raise ValueError
        except (ValueError, EOFError):
            print("Invalid input, try again.")
            continue

        if choice == 0:
            print(f"\nLogged out. Goodbye, {trainer.name}!")
            break

        elif choice == 1:
            try:
                print("\n=== View Schedule ===")
                sessions = trainer.get_schedule(db=db)
                if not sessions:
                    print("No sessions found.")
                    continue
                for session in sessions:
                    print(
                        f"  Class {session.id}: {get_day_name(session.day_of_week)} | {session.start_time} - {session.end_time} "
                        f"| Name: {session.name} "
                        f"| Room: {session.room_id or 'N/A'}"
                    )
            except Exception as e:
                print(f"\n✗ Error: {e}")

        elif choice == 2:
            print("\n=== Set Availability ===")
            while True:
                print("\nDays of the week:")
                print("  1: Monday")
                print("  2: Tuesday")
                print("  3: Wednesday")
                print("  4: Thursday")
                print("  5: Friday")
                print("  6: Saturday")
                print("  7: Sunday")
                print("  0: Finish")
                try:
                    day_input = int(input("Enter day (0 to Finish): ").strip())
                    if day_input == 0:
                        break
                    if not (1 <= day_input <= 7):
                        print("Invalid day. Please enter 1-7.")
                        continue
                    
                    start_time = prompt_time("Start time")
                    end_time = prompt_time("End time")
                    
                    window = trainer.set_availability(
                        db=db, 
                        day_of_week=day_input, 
                        start_time=start_time, 
                        end_time=end_time
                    )
                    print(
                        f"Availability set for {get_day_name(window.day_of_week)}: "
                        f"{window.start_time} - {window.end_time} (Window ID: {window.id})"
                    )
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")

        elif choice == 3:
            try:
                print("\n=== Member Lookup ===")
                name = input("Enter member name: ").strip()
                if not name:
                    raise ValueError("Name cannot be empty.")
                member = trainer.lookup_member(db=db, name=name)
                if member is None:
                    print("Member not found.")
                    continue
                print(f"\nMember: {member.name}")
                print(f"  Email: {member.email}")
                print(f"  Age: {member.age if member.age is not None else 'N/A'}")
                print(f"  Gender: {member.gender or 'N/A'}")
                print(f"  Weight Goal: {member.weight_goal if member.weight_goal is not None else 'N/A'} kg")
            except ValueError as e:
                print(f"\nError: {e}")
            except Exception as e:
                print(f"\nUnexpected error: {e}")

        elif choice == 4:
            try:
                print("\n=== My Availability ===")
                availabilities = trainer.get_availability(db=db)
                if not availabilities:
                    print("No availability set.")
                else:
                    for avail in availabilities:
                        print(
                            f"  {get_day_name(avail.day_of_week)}: {avail.start_time} - {avail.end_time}"
                        )
            except Exception as e:
                print(f"\nError: {e}")

def main():
    # while loop allows us to exit back to role selection
    while True:

        # ask user for their role
        try:
            prompt = (
                "\nSelect role:\n"
                "\t0 - Exit\n"
                "\t1 - Admin\n"
                "\t2 - Trainer\n"
                "\t3 - Member\n"
                "Enter choice: "
            )
            role = int(input(prompt))
            if role not in range(0,4):
                raise ValueError

        except (ValueError, EOFError):
            print("Invalid input, try again.")
            continue

        if role == 0:
            print("Exiting...")
            break

        elif role == 1:
            admin_menu()

        elif role == 2:
            trainer_menu()

        elif role == 3:
            member_menu()
        else:
            print("Unknown role, try again.")


if __name__ == "__main__":
    main()
