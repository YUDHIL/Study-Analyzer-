# Study Analyzer: Implementation Plan for Google Antigravity

## 1. Project Overview

**Project name:** Study Analyzer  
**Type:** Personal productivity and academic analytics web application  
**Goal:** Help a student manage semester exam preparation, track daily study sessions, improve Python coding skills, and analyse progress using data-driven insights.

Build a complete, functional application, not just a static dashboard or UI prototype.

The application must work locally on Windows 11, use a local SQLite database, preserve data between sessions, and have a modern dark-mode interface.

### Requirements

- Track five semester subjects.
- Semester examination period: November 17–30, 2026.
- Daily study planner and task completion tracking.
- Syllabus and topic completion tracking.
- Actual study time logging.
- Test marks and performance analysis.
- Python coding practice and independent problem-solving tracking.
- Weekly analytics and actionable recommendations.
- Beginner-friendly code structure so the student can understand and modify the application.

## 2. Technology Stack

- **Python:** Application logic and analytics.
- **Streamlit:** Interactive web dashboard and forms.
- **SQLite:** Persistent local database.
- **Pandas:** Data analysis and aggregation.
- **Plotly:** Interactive charts.
- **Python datetime:** Date calculations and study scheduling.
- **pytest:** Basic automated testing.

Keep the application local-first. Do not require cloud hosting, paid APIs, authentication services, or external AI APIs for the core features.

## 3. Application Structure

Create this maintainable project structure:

```text
study-analyzer/
├── app.py
├── database.py
├── analytics.py
├── recommendations.py
├── requirements.txt
├── README.md
├── .gitignore
├── pages/
│   ├── 1_Daily_Planner.py
│   ├── 2_Subjects_and_Topics.py
│   ├── 3_Study_Log.py
│   ├── 4_Test_Performance.py
│   ├── 5_Python_Practice.py
│   └── 6_Weekly_Analytics.py
├── components/
│   ├── sidebar.py
│   ├── metrics.py
│   └── charts.py
├── tests/
│   ├── test_database.py
│   └── test_analytics.py
└── data/
    └── .gitkeep
```

Create the SQLite database automatically inside `data/` on first run. Ensure the directory exists before connecting.

## 4. Dashboard and UI Design

Create a professional, modern, dark-themed dashboard inspired by developer productivity tools.

### Visual requirements

- Deep navy or charcoal background.
- Subtle borders and dark cards.
- Clear typography and consistent spacing.
- Blue, teal and green accents.
- Rounded metric cards.
- Interactive charts with dark backgrounds.
- Responsive layout for laptops and smaller screens.
- Sidebar navigation with icons.
- Consistent design across pages.
- Helpful empty states when no data has been entered.
- Success and error messages after user actions.

Avoid excessive gradients, unnecessary animations, cluttered layouts, and decorative charts that do not communicate useful information.

### Dashboard layout

At the top, show:

1. Welcome message and current date.
2. Days remaining until the next configured examination.
3. Total study hours.
4. Syllabus completion percentage.
5. Average test score.
6. Python problems solved independently.

Below the metric cards, show:

- Subject-wise syllabus completion.
- Daily study hours for the last seven days.
- Today's planned tasks and their status.
- Upcoming examinations.
- Weak topics requiring revision.
- A recommended next study task.
- Coding progress summary.

Every metric and chart must use actual database records. Never use hardcoded demonstration values after initialization.

## 5. Database Design

Implement a normalized SQLite schema with appropriate primary keys, foreign keys, constraints, and indexes.

### Subjects

Fields:

- `id`
- `name`
- `exam_date`
- `target_hours`
- `created_at`

Allow users to create, rename, and safely remove subjects. Start with five editable placeholders and let the user enter actual subject names and examination dates.

Do not assume that all five examinations occur on November 17. The overall exam period is November 17–30, 2026; individual dates must be configurable.

### Topics

Fields:

- `id`
- `subject_id`
- `unit_name`
- `topic_name`
- `status`
- `confidence`
- `created_at`
- `updated_at`

Supported statuses:

- Not Started
- In Progress
- Completed
- Needs Revision

Confidence is rated from 1 to 5.

Prevent duplicate topics within the same subject and unit where appropriate.

### Tasks

Fields:

- `id`
- `task_date`
- `title`
- `category`
- `subject_id` (nullable)
- `planned_minutes`
- `priority`
- `completed`
- `completed_at`
- `created_at`

Task categories should include:

- Semester Study
- Revision
- Practice Test
- Python Coding
- DSA Practice
- Project Work

Support adding, editing, completing, and deleting tasks.

### Study Logs

Fields:

- `id`
- `study_date`
- `subject_id` (nullable for non-academic sessions)
- `topic`
- `minutes`
- `understanding`
- `notes`
- `created_at`

Validate that study duration is positive and reasonable. Record actual sessions independently of planned tasks.

### Test Results

Fields:

- `id`
- `test_date`
- `subject_id`
- `test_name`
- `score`
- `max_score`
- `notes`
- `created_at`

Validate that maximum marks are positive and scores are between zero and maximum marks.

Calculate percentages using each test's score divided by its maximum marks. For aggregate performance, distinguish between the average of test percentages and the weighted percentage calculated from total marks.

### Coding Logs

Fields:

- `id`
- `practice_date`
- `problem_name`
- `concept`
- `platform`
- `attempted`
- `solved`
- `independent`
- `hints_used`
- `minutes`
- `notes`
- `created_at`

Track attempts, successful solutions, and solutions completed without viewing the answer. A problem counts as independently solved only when the user confirms they solved it without viewing a solution.

Use parameterized SQL queries, context-managed connections, explicit transaction handling where appropriate, and clear error messages.

## 6. Feature Implementation

### Module A: Daily Planner

Create a functional daily planning page.

Requirements:

- Select a date.
- Add a task and choose its category.
- Associate a task with a subject when relevant.
- Enter estimated duration and priority.
- Display today's tasks.
- Mark tasks as completed.
- Edit or delete tasks.
- Display planned versus completed task counts.
- Display planned minutes versus actual logged study minutes.
- Filter tasks by date, category, and subject.
- Show overdue tasks without changing their original dates.
- Preserve changes in SQLite.

Provide an optional button to create a daily plan using a simple, explainable priority algorithm. The user must remain able to edit the generated plan.

### Module B: Subject and Topic Tracker

Requirements:

- Create and edit subjects.
- Configure individual examination dates.
- Add topics and units.
- Change topic status.
- Update confidence ratings.
- Filter topics by subject, unit, and status.
- Display topic counts and completion percentages.
- Identify topics marked Needs Revision.
- Allow safe deletion with confirmation.

Completion percentage must be calculated from completed topics, not estimated from study hours.

If a subject has no topics, display completion as 0% and explain that topics need to be added.

### Module C: Study Log

Requirements:

- Record date, subject, topic, and duration.
- Add understanding ratings and notes.
- Display recent study sessions.
- Edit or delete incorrect entries.
- Filter by date range and subject.
- Calculate daily and weekly study totals.
- Compare planned time with actual study time.

Use actual study logs for time-based analytics. Do not infer actual study time from completed tasks.

### Module D: Test Performance

Requirements:

- Add test name, date, subject, score, and maximum marks.
- Display test history.
- Calculate percentages.
- Show subject-wise performance.
- Show performance trends over time.
- Identify subjects with lower scores.
- Allow editing and deletion.
- Show a useful empty state when no tests have been recorded.

Do not label a subject as academically weak solely because it has fewer tests. Indicate when data is insufficient.

### Module E: Python Practice Tracker

Requirements:

- Record problem name and programming concept.
- Record platform, practice date, and time spent.
- Track whether the problem was attempted and solved.
- Track whether it was solved independently.
- Record hints used and learning notes.
- Display attempted, solved, and independently solved totals.
- Calculate the independent-solve rate using a clearly defined denominator.
- Display progress by topic, such as loops, strings, lists, dictionaries, functions, and recursion.
- Identify problems that need another attempt.

Do not automatically classify a solution as independent just because the user marked the problem solved.

### Module F: Weekly Analytics

Create a selectable seven-day report with:

- Total study hours.
- Study hours by subject.
- Daily study duration chart.
- Planned versus actual study time.
- Task completion rate.
- Topics completed.
- Test performance changes.
- Python problems attempted and solved.
- Independent coding performance.
- Comparison with the previous seven-day period when sufficient data exists.

Use consistent date boundaries and handle weeks with missing data correctly.

Provide filters where useful. Avoid misleading percentage changes when the previous period has zero activity.

### Module G: Recommendation Engine

Create a separate `recommendations.py` module using transparent rule-based logic.

Recommendations should consider:

1. Days remaining until each configured examination.
2. Number of unfinished topics.
3. Topics marked Needs Revision.
4. Confidence ratings.
5. Available test results.
6. Planned and actual study time.
7. Uncompleted high-priority tasks.
8. Python practice progress.

Example recommendation:

"Subject 2 has an examination approaching, and several topics remain unfinished. Complete one high-priority topic and revise one weak topic today."

Another example:

"You attempted five Python problems but solved only one independently. Reattempt two previously viewed problems without opening the solutions."

Recommendations must explain their reasons. Do not fabricate performance information or promise a particular examination score.

If the user has not entered enough data, recommend adding subjects, topics, or study logs before generating more specific advice.

## 7. Exam Preparation Configuration

Set the default examination window to:

- Start: November 17, 2026.
- End: November 30, 2026.

Make the dates configurable in the application.

Create a preparation dashboard that:

- Shows upcoming configured exam dates.
- Sorts subjects by urgency and preparation needs.
- Highlights incomplete and weak topics.
- Supports a daily academic study target.
- Supports a smaller daily coding target.
- Allows a revision period before each examination.
- Reduces optional coding workload during the examination period when requested by the user.

Do not invent subject names, examination schedules, or syllabus contents.

## 8. Analytics Definitions

Use explicit, consistent formulas.

**Syllabus completion**

Completed topics / Total topics × 100.

**Test percentage**

Score / Maximum score × 100.

**Task completion rate**

Completed tasks / Total scheduled tasks × 100.

Clearly label the selected date range and handle empty denominators safely.

**Independent coding rate**

Independently solved problems / Attempted problems × 100, with the denominator explicitly defined in the UI. Prefer a clearly documented, consistent interpretation based on recorded attempts.

**Study consistency**

Number of days meeting the configured study target / Number of elapsed days in the selected period × 100.

Do not treat future days as missed study days. Allow the user to change the target.

For comparisons, show raw totals alongside percentages so numbers remain interpretable.

## 9. Reliability, Privacy and Data Safety

- Store all user records locally in SQLite.
- Never transmit personal study data to an external service.
- Add database initialization and schema migration handling.
- Use parameterized SQL for every user-supplied value.
- Validate form inputs.
- Handle empty databases and missing data safely.
- Add confirmation dialogs before destructive actions.
- Preserve records when switching pages or restarting the application.
- Provide a database backup and restore feature.
- Validate uploaded backup files before restoring.
- Avoid overwriting an existing database during restoration without confirmation.
- Add `.venv/`, database files, and temporary files to `.gitignore`.
- Keep dependencies in `requirements.txt`.
- Keep error messages useful without exposing sensitive internals.

## 10. Testing Requirements

Write automated tests for:

- Database initialization.
- Subject and topic creation.
- Task completion and editing.
- Study log insertion.
- Test percentage calculations.
- Topic completion calculations.
- Weekly aggregation.
- Independent coding statistics.
- Empty datasets.
- Invalid marks and durations.
- Data persistence between database connections.

Use a temporary SQLite database in tests so testing never alters the user's real study records.

## 11. Beginner-Friendly Implementation Workflow

Implement the project incrementally in this order.

### Phase 1: Foundation
- Create the folder structure.
- Set up dependencies.
- Build the SQLite schema.
- Verify database persistence.

### Phase 2: Core dashboard
- Build the sidebar.
- Add summary cards.
- Add subject progress charts.
- Add empty states.

### Phase 3: Study management
- Implement subject management.
- Implement topic management.
- Implement the daily planner.
- Implement study logging.

### Phase 4: Performance tracking
- Implement test results.
- Implement Python practice logs.
- Implement weekly analytics.

### Phase 5: Intelligence
- Add rule-based recommendations.
- Add examination urgency calculations.
- Add revision suggestions.

### Phase 6: Quality
- Add backup and restore.
- Add automated tests.
- Validate the UI.
- Document setup and usage.

After each phase, run the application, verify the feature, and fix errors before moving on.

Because the user is learning Python, provide short explanations of important functions, database operations, and calculations. Avoid unnecessarily advanced abstractions. Keep the code readable and modular.

## 12. Definition of Done

The project is complete only when:

- The application starts with one documented command.
- All seven pages work.
- Subjects, topics, tasks, study sessions, test results, and coding records can be created and edited.
- Changes persist after restarting the application.
- Dashboard metrics match underlying database records.
- Weekly analytics use the selected date range correctly.
- Recommendations are based on recorded data.
- The interface consistently uses the dark theme.
- Automated tests pass.
- The README includes installation, launch, backup, and troubleshooting instructions.

## Final Instruction to Antigravity

Inspect the current project before making changes. If no project exists, create the structure described above.

Implement the project in small, verifiable milestones. Do not stop after producing a plan, wireframe, or static mockup. Write the actual files, run the application and tests where execution is available, inspect errors, and fix them.

Do not silently replace existing files or discard existing user data. Explain any limitations and report which features have actually been implemented and tested.

The final result should be a functional, maintainable, beginner-friendly personal Study Analyzer that supports academic preparation and independent Python skill development.
