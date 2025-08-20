# Game Design Document: Tap Ninja Support Tool

---

## 1. Document Version
**Version:** 1.0
**Date:** August 19, 2025

---

## 2. Application Overview

### 2.1. Application Name
Tap Ninja Helper (TNH)

### 2.2. Genre
Game Utility, Supporting Application

### 2.3. Target Audience
Players of the 2D idle game "Tap Ninja" who are looking to optimize their gameplay and automate progress tracking.

### 2.4. Core Concept
Tap Ninja Helper is a desktop application designed to assist players of "Tap Ninja". It works by taking screenshots of the game window, using Optical Character Recognition (OCR) to read key numerical data, and then providing users with valuable calculations and estimations. This allows players to make more informed decisions about their in-game strategy without manual calculations.

---

## 3. Core Features

### 3.1. Screen Capture Module
*   **Functionality:** The application will have the ability to capture a user-defined area of the screen.
*   **Implementation:** Users can select the "Tap Ninja" game window or a specific portion of it for the application to monitor. The application will take screenshots at user-defined intervals or on-demand.

### 3.2. OCR (Optical Character Recognition) Module
*   **Functionality:** To read and convert numbers from the captured screenshots into machine-readable data.
*   **Implementation:** The OCR engine will be trained or configured to recognize the specific fonts and number formats used in "Tap Ninja" for values such as:
    *   Gold
    *   Elixir
    *   Amber
    *   Current level
    *   Upgrade costs

### 3.3. Calculation & Estimation Module
*   **Functionality:** This is the core of the application, providing users with useful insights.
*   **Calculations:**
    *   **Gold Per Minute (GPM):** Tracks the change in gold over time to calculate the GPM.
    *   **Time to Next Upgrade:** Based on the current GPM and the cost of a desired upgrade, the application will estimate the time remaining to afford it.
    *   **Efficiency Calculator:** Potentially compare the cost vs. benefit of different upgrades to suggest the most efficient path.

### 3.4. User Interface (UI)
*   **Dashboard:** A simple and clean interface that displays the extracted data and the results of the calculations.
*   **Configuration:** A settings panel where users can define the screen capture area, hotkeys, and the frequency of data updates.
*   **Overlay Mode (Optional):** A potential feature to overlay the calculated data on top of the game window for easy viewing.

---

## 4. Technical Specifications

### 4.1. Platform
*   **Primary:** Windows Desktop

### 4.2. Key Technologies & Libraries
*   **Programming Language:** Python
*   **GUI Framework:** Tkinter, PyQt, or a similar library for the user interface.
*   **Screen Capture:** A library like `Pillow` or `pyautogui`.
*   **OCR:** `Tesseract` (via `pytesseract`) or other suitable OCR libraries.

---

## 5. UI/UX Flow

1.  **Initial Setup:**
    *   On the first launch, the user is prompted to select the "Tap Ninja" game window or draw a rectangle around the game area.
    *   The user is then guided to areas on the screen to identify where key information (like Gold, Elixir, etc.) is displayed.

2.  **Main Application Loop:**
    *   The user starts the monitoring process via a "Start" button in the UI.
    *   The application begins taking screenshots at the set interval.
    *   The OCR module processes these screenshots to extract the latest numerical values.
    *   The calculation module updates the displayed estimations (GPM, time to upgrade, etc.).

3.  **User Interaction:**
    *   The user can view the live-updated data on the application's dashboard.
    *   The user can pause the monitoring at any time.
    *   The user can reconfigure the capture area and other settings as needed.

---

## 6. Monetization
This will be a free-to-use application. Monetization is not a primary goal. It could be released as an open-source project to the "Tap Ninja" community.

---

## 7. Future Scope
*   **Advanced Analytics:** Tracking progress over longer periods and providing graphical representations of earnings and progress.
*   **Automated Upgrade Suggestions:** Implementing a more intelligent system to recommend the best upgrades based on user-defined goals.
