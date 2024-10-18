# MDP Admin Panel for Vishvas News

This is the Admin panel for the Multimodal Data Processing (MDP) system of Vishvas News, built in collaboration with IIT Kharagpur.

## Frontend Setup

### To run the frontend locally:

1. Install the required packages:
   ```bash
   npm install --legacy-peer-deps
   ```

2. Start the development server:
   ```bash
   npm start
   ```

   The frontend will launch on **port 5000**.

### Testing Frontend Code Locally

If you want to test the frontend code locally but need to point to live API endpoints, update the API calls by replacing relative URLs with full URLs. For example:

```diff
- fetch("/api/ensemble", {
+ fetch("https://factchecker.vishvasnews.com/api/ensemble", {
```

## Backend Setup

### To run the backend:

1. Install the required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend:
   ```bash
   python3 app.py
   ```

### Troubleshooting

- If you encounter any issues while installing dependencies, try installing the required packages one by one.
- If you encounter errors related to **IndicTrans not found**, download the `IndicTrans2` folder from the VM and place it in the correct directory.

