
``` mermaid
classDiagram
    class Owner {
        -owner_id: string
        -name: string
        -email: string
        -phone: string
        -pets: Pet[]
        +add_pet(pet: Pet)
        +remove_pet(pet_id: string)
        +get_all_pets() Pet[]
        +update_contact_info(email, phone)
        +get_pet_by_id(pet_id) Pet
    }

    class Pet {
        -pet_id: string
        -name: string
        -species: string
        -breed: string
        -age: int
        -weight: float
        -birth_date: date
        -owner_id: string
        -medications: string[]
        +get_info() string
        +update_weight(new_weight)
        +add_medical_record(record)
        +get_age() int
        +is_on_medication() bool
    }

    class Task {
        -task_id: string
        -task_type: enum
        -pet_id: string
        -description: string
        -scheduled_date: date
        -scheduled_time: time
        -priority: enum
        -status: enum
        -completion_timestamp: datetime
        +mark_complete(timestamp)
        +mark_missed()
        +reschedule(new_date, new_time)
        +is_overdue(current_time) bool
        +get_details() string
        +set_reminder(time_before)
    }

    class Scheduler {
        -tasks: Task[]
        -owner_id: string
        -recurring_tasks: Task[]
        +create_task(pet_id, task_type, description, date, time)
        +get_tasks_for_pet(pet_id) Task[]
        +get_tasks_for_date(date) Task[]
        +get_today_tasks() Task[]
        +get_overdue_tasks() Task[]
        +get_completed_tasks(pet_id, date_range) Task[]
        +complete_task(task_id)
        +reschedule_task(task_id, new_date, new_time)
        +create_recurring_task(pet_id, task_type, days_of_week, time)
        +get_upcoming_week() Task[]
        +generate_report(pet_id) string
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    Scheduler "1" --> "*" Task : manages
    Scheduler "1" --> "1" Owner : belongs_to
    ```
    