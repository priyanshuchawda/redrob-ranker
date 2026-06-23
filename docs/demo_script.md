# Two Minute Judge Demo

1. Start the backend:

   ```powershell
   uvicorn api.main:app --reload
   ```

2. Start the frontend:

   ```powershell
   cd frontend
   npm run dev
   ```

3. Open `http://localhost:3000` and enter the Recruiter Intelligence Console.

4. Open Dashboard and confirm total candidates, shortlisted candidates, average confidence, high-risk profiles, runtime, leaderboard, score breakdown, risk radar, and evidence preview.

5. Open Run Ranking and use the demo JD/candidates or paste new JSON/JSONL candidate data.

6. Open the top candidate detail page and show why shortlisted, best evidence, main concern, why not ranked higher, interview focus, positive evidence, missing evidence, and risk flags.

7. Open Compare and compare `CAND_DEMO_001` versus `CAND_DEMO_002`.

8. Open Exports and show JSON/CSV export endpoints.

9. In the terminal, run:

   ```powershell
   python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 3
   python evaluate.py --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md --top-n 4
   ```

10. Show `outputs/evaluation_report.md` and note that it is proxy evaluation unless labels are supplied.
