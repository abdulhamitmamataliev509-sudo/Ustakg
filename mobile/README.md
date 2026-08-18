# Usta kg — Mobile (Phase 5)

This folder contains the Expo React Native app scaffold for Phase 5 (Mobile App Foundation).

Key points:
- Uses `zustand` for auth state
- Centralized Axios client in `src/services/api.js`
- Navigation stacks and tab navigators in `src/navigation/`
- Screens for Customer and Master flows under `src/screens/`

To run locally:

1. Install dependencies:
```bash
cd mobile
npm install
```

2. Start Expo:
```bash
npm start
```

Notes:
- Ensure backend API is reachable. Adjust base URL in `src/config.js` for simulator/emulator.
