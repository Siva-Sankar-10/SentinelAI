# SentinelAI Project Audit

## 1. Folder explanation

### Root project structure

- app.py
  - Main Flask application entry point.
  - Defines routes, dashboard/report logic, database interaction, error handlers, model loading, and application startup.

- database.py
  - SQLite database bootstrap and legacy schema migration helper.
  - Creates or repairs the history table used by the dashboard.

- train_model.py
  - Offline model training pipeline.
  - Loads NSL-KDD data, encodes categorical variables, trains a Random Forest classifier, evaluates it, and saves model artifacts.

- predict.py
  - Standalone prediction helper for a model bundle.
  - Loads a saved object dictionary and provides a reusable prediction function.

- requirements.txt
  - Python dependencies for the project.

- dataset/
  - Training/evaluation data source.
  - Contains the NSL-KDD dataset text files used by the training workflow.

- uploads/
  - Stores uploaded dataset files submitted via the web form.

- reports/
  - Stores generated PDF reports.

- static/
  - Frontend assets used by the templates.
  - Includes CSS, JavaScript, and imagery for the UI.

- templates/
  - Flask Jinja HTML templates.
  - Implements the pages shown to users: landing page, upload page, dashboard, history, about, login, loading UI, error pages, and result page.

- models/
  - Intended storage for model-related assets and supporting folders.

- sentinel.db
  - SQLite database file storing analysis history data.

- model.pkl, protocol_encoder.pkl, service_encoder.pkl, flag_encoder.pkl, sentinel_model.pkl
  - Serialized ML artifacts.
  - These are the runtime model and encoder objects used by the Flask app.

- test.py, test1.py, check.py, check_dataset.py, _check_error.py, _check_error2.py, _check_error3.py, _check_template.py
  - Debugging, validation, or development support scripts.
  - They are not core to the production route flow.

---

## 2. Purpose of every major file

### app.py
Purpose:
- Flask server entry point.
- Creates app state, config, and model loading.
- Implements user-facing route handlers for:
  - home
  - about
  - upload
  - dashboard
  - history
  - prediction
  - report download
  - history clearing
  - report deletion
  - reset
- Handles exceptions and displays human-readable error pages.

### database.py
Purpose:
- Initializes the SQLite `history` table.
- Performs schema migration from older legacy field names to the current normalized schema.

### train_model.py
Purpose:
- Builds the intrusion-detection model from the NSL-KDD dataset.
- Saves trained model objects using `joblib`.
- Produces metrics such as accuracy, classification report, confusion matrix, and feature importance.

### predict.py
Purpose:
- A separate utility module for predicting on datasets using the saved model bundle.
- Reads the saved objects and applies encoding/feature selection before inference.

### requirements.txt
Purpose:
- Declares the runtime dependencies needed by the Flask site and model pipeline.

### templates/base.html
Purpose:
- Shared layout shell for every page.
- Provides common navigation, footer, page title block, JS/CSS references, and animated system styling.

### templates/index.html
Purpose:
- Marketing/landing page.
- Introduces the application and presents the call to action for dataset upload.

### templates/upload.html
Purpose:
- Dataset upload UI.
- Supports drag-and-drop and client-side file validation.
- Posts form data to the `/predict` route.

### templates/dashboard.html
Purpose:
- Main analysis result dashboard.
- Displays counts, threat classification, uploaded file metadata, charts, and recent history.

### templates/history.html
Purpose:
- Historical analysis page.
- Displays all analysis results in a searchable table and chart trend view.

### templates/about.html
Purpose:
- Explains the system concept and security context.

### templates/login.html
Purpose:
- Login page stub.
- Not tied into the backend authentication flow in the current implementation.

### templates/loading.html
Purpose:
- Loading/transition screen concept.
- Helps present a progress-style UI while upload/prediction is happening.

### templates/result.html
Purpose:
- Result display page placeholder for a more structured post-analysis screen.

### templates/404.html
Purpose:
- Not-found page.

### templates/500.html
Purpose:
- Generic internal server error page.

### static/css/style.css
Purpose:
- Core visual theme for the project.
- Defines color palette, animations, layout, cards, text styling, and premium cyber-security look.

### static/css/animations.css
Purpose:
- Supplemental motion/transition definitions for the frontend.

### static/js/main.js
Purpose:
- Main site-level interactivity.
- Handles live clock, typing animation, counters, navbar scroll effect, mouse glow, and terminal-style log animation.

### static/js/particles-config.js
Purpose:
- Particle background configuration used to create the animated background effect.

### static/js/ai-core.js
Purpose:
- Three.js-based visualization of an animated AI/security-themed 3D object for the landing page or interface shell.

---

## 3. Data flow

### End-to-end flow

1. User visits the site and lands on the homepage.
2. User goes to `/upload` and selects a dataset.
3. Browser submits the file to the Flask route `/predict`.
4. The backend validates the incoming file and file extension.
5. File is saved into the `uploads/` folder.
6. The CSV/TXT dataset is read into a Pandas DataFrame.
7. Columns are assigned to the NSL-KDD schema.
8. Categorical columns are encoded using pretrained LabelEncoder objects.
9. The model predicts whether each record is normal or attack.
10. Counts are aggregated into:
    - total
    - attack
    - normal
    - threat level
11. The results are stored in memory as `REPORT_DATA` and persisted into the `history` table in SQLite.
12. User is redirected to the dashboard.
13. Dashboard queries recent history and renders KPI cards, charts, and file metadata.
14. PDF report can be downloaded using `/download_report`.
15. History can be explored through `/history` and optionally cleared using `/clear_history`.

### Internal model data flow

- `train_model.py` trains and persists the artifacts.
- `app.py` loads the saved model and encoders at startup.
- Uploaded CSV/TXT data is transformed to match the training feature space.
- Predictions are computed using the loaded Random Forest model.

---

## 4. Architecture diagram (text)

```text
User Browser
    |
    v
Flask App (app.py)
    |-- route: /
    |-- route: /upload
    |-- route: /predict
    |-- route: /dashboard
    |-- route: /history
    |-- route: /download_report
    v
Upload Validation + Dataset Save
    |
    v
Pandas DataFrame
    |
    v
Feature Encoding (protocol_type, service, flag)
    |
    v
Random Forest Model (model.pkl)
    |
    v
Prediction Summary
    |
    +--> app.config["REPORT_DATA"]
    |
    +--> SQLite table: history
    |
    +--> Jinja Templates
           |
           +--> dashboard.html
           +--> history.html
           +--> index.html
           +--> upload.html

Static assets:
static/css/style.css
static/js/main.js
static/js/particles-config.js
static/js/ai-core.js
```

---

## 5. List every bug found

### Backend and logic bugs

1. Upload field mismatch
   - The form posts `file`, while the Flask route reads `dataset` in some code paths.
   - This breaks the request contract unless the route is made compatible.

2. Database schema mismatch
   - `database.py` creates a `history` table using fields like `filename` and `date`.
   - `app.py` expects `file_name`, `threat`, and `upload_time`.
   - This creates unstable history behavior and inconsistent persistence contracts.

3. Legacy table migration is incomplete and fragile
   - The migration depends on `filename` and `date` existing in the legacy table.
   - It does not robustly handle all historical schema versions.

4. Hardcoded model accuracy
   - The app assigns `accuracy = 99.42` as a fixed value.
   - This is not the real evaluated model accuracy from the training run.

5. Incorrect/unsafe categorical encoding assumption
   - The model expects learned encoders, but raw uploaded data may contain unseen values.
   - The application does not fully validate unknown categories before transform.

6. Overly permissive global exception handler
   - `@app.errorhandler(Exception)` catches all exceptions and redirects to `/`.
   - This can mask real bugs and hide important diagnostics from the user.

7. History page chart variables are not populated properly in the route
   - The chart data is referenced in template code, but the route may not populate the full chart object needed for rendering.

8. Error templates for 403 and 405 are never present in the templates folder
   - The handlers reference `403.html` and `405.html`, but the repository does not contain those templates.

9. No proper file overwrite protection
   - Uploaded files are stored by plain filename in `uploads/`.
   - If the same file name is uploaded twice, the file can be overwritten without a collision strategy.

10. No real authentication or authorization
    - There is a login page stub and mention of admin dashboard, but no actual authentication or role enforcement exists.

### Frontend contract bugs

11. Upload UI advertises `.txt` support, but the backend historically only accepted `.csv`.
12. The home page and some JS references imply a richer AI console, but large parts of the runtime are still demo/prototype oriented.

---

## 6. Security issues

### High priority

- Hardcoded secret key in `app.py`
  - `app.secret_key = "sentinel_ai_secret_key"` is embedded in source code.
  - This is a poor security practice for production environments.

- No authentication system
  - The project exposes a file upload and analysis workflow without any identity verification.
  - This is a serious access-control gap.

- No authorization boundaries
  - Anyone who can reach the web endpoint can upload and trigger analysis.

- File upload without sanitization strategy
  - User uploads are saved directly to `uploads/` without rigorous validation beyond extension checking.
  - This creates opportunities for unsafe file content and path-confusion issues.

- No CSRF protection
  - The form submission pattern is not protected with a CSRF token or a session-based anti-forgery strategy.

- No secret management
  - Config values such as the Flask secret key are not externalized.

### Medium priority

- SQLite database is plain file storage.
  - No encryption-at-rest or hardened access controls are described.

- No rate limiting or request throttling.
  - This may allow resource exhaustion under repeated uploads.

- No audit trail for user actions.
  - Only a simple history of analysis records exists, not permissioned security event logging.

---

## 7. Performance issues

- The app loads the full model into memory at import time.
  - This is acceptable for prototyping but may scale poorly if many users upload concurrently.

- Uploaded datasets are read fully into memory with Pandas.
  - Large CSV files can become expensive quickly.

- The dashboard and history endpoints access the SQLite database without any indexing strategy or query optimization.
  - This may become slow on large history tables.

- PDF report generation uses ReportLab table creation for every request.
  - This is okay for small usage, but may be slower under heavier load.

- Multiple JS components initialize animations and particle effects on every page.
  - Unnecessary front-end load can affect experience on low-powered devices.

- The app reruns an end-to-end dataload and prediction pipeline per upload with no background worker separation.
  - This can create a blocking request-time path for more complex workloads.

---

## 8. Code duplication

There are several repeated or overlapping patterns in the codebase:

1. Model-saving logic is duplicated between training and runtime serialization.
   - `train_model.py` saves both a bundle object and individual encoders/model files.

2. Database creation logic is duplicated in style and intent.
   - `app.py` and `database.py` both attempt to create or manage the history table.

3. Similar route and UI components are repeated across templates.
   - Different pages share nearly identical structure and presentation choices with repeated cards, badges, and page-header blocks.

4. There are multiple inspect/debug helper scripts that overlap in purpose.
   - `_check_error.py`, `_check_error2.py`, `_check_error3.py`, and other test utilities are not clearly integrated into the production app flow.

5. Chained chart and status UI code is present in several templates, creating a non-centralized frontend pattern.

---

## 9. Recommended improvements

### Immediate fixes

- Standardize the upload field name so that the HTML and Flask route agree.
- Consolidate the `history` schema into one canonical definition.
- Replace the hardcoded accuracy with a measured value from the model evaluation or an actual validation dataset.
- Add proper handling for unknown categorical labels instead of relying on fallback behavior.
- Implement 403/405 templates or remove the handlers if route handlers are not needed.

### Security improvements

- Move the Flask secret key into environment variables.
- Add a real login and RBAC model.
- Add CSRF protection to the form workflow.
- Add file upload validation beyond extension checks.
- Use secure storage and permission control for database and upload artifacts.

### Architecture improvements

- Split the app into reusable services:
  - dataset ingestion
  - preprocessing
  - model inference
  - persistence
  - report rendering
- Replace ad hoc file-based app state with a well-defined configuration object or dependency container.
- Add unit/integration tests for the prediction, dashboard, and history flow.

### Performance improvements

- Add pagination for history queries.
- Use database indexes on frequently filtered columns.
- Move long-running prediction jobs into a background worker or job queue.
- Add streaming or chunk-based dataset processing for large files.

### Frontend improvements

- Remove duplicate CSS/JS includes from templates.
- Centralize chart and dashboard logic into a single helper or component file.
- Use a dedicated JavaScript module for upload UX rather than inline script blocks.

### ML improvements

- Store the full model metadata with versioning.
- Save the train/test split metadata and evaluation metrics alongside the model.
- Add confidence scores and class probability output to the dashboard.
- Use a more explicit attack-vs-normal evaluation rather than a binary rule-of-thumb threat percentage.

---

## Final assessment

SentinelAI is a strong prototype for an IDS demo application:

- It has a polished appearance.
- It uses real Flask and ML concepts.
- It visualizes intrusion-detection analysis through a dashboard.
- It persists summary history in SQLite.

However, the current implementation is still more of a polished demo than a production-grade application. The biggest risk areas are schema inconsistency, weak security posture, hardcoded aggregate metrics, and fragile upload assumptions. Those should be addressed before the project is treated as a dependable backend service.
