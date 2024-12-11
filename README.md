install tailwind and run

```
./tailwindcss-windows-x64.exe -i ./tournaments/static/tournaments/css/input.css -o ./tournaments/static/tournaments/css/output.css --watch
```


## Roadmap
- A user can see the tournaments list
  - See a blank page with no tournaments ✅
  - See one tournament ✅
  - See many tournaments ✅
  - Will never see a tournaments with the same name twice ✅


- A User can see the stages of a tournament ✅
  - See a blank page with no stages ✅
  - See 1 stage ✅
  - see many stages ✅
  - Will never see a stage with the same name twice ✅


- A user can see the list of matches
  - See a blank page with no matches ✅
  - A User can see a match ✅
  - A User can see a list of matches ✅
  - Matches are unique 
    -  Will never see Round of 16 match 1 twice ✅
  - Runner-up Group A vs Runner-up Group B is a valid match ✅
  - A match can be shown without teams ✅
  - A match that didn't end yet, will show the teams without the score ✅
  - A match that ended will show the teams with the score ✅
  - Hide # ✅
  - Show date and time ✅

  
- Match predictions
  - See a blank page with no predictions ✅
  - See one friend's prediction ✅
  - See multiple friend predictions ✅
  - If the game is not scored yet, show zero points ✅
  - If the game is scored, show the score for each prediction ✅
  - Default order by points ✅
  - User can change order ✅
  - Statistics
    - How many friends participated, guessed, hit ✅



- Stage points
  - very similar to the match predictions ✅
  - Show Matches ✅
  - Show Group Table 
  - Show stage statistics


- Match stats ✅
  - Results: Bullseye, Hit, Wrong, Didn't play ✅
  - If match didn't start yet, let's not do it. ✅
  - 1/3 should be 33.33% ✅
  - 1 should be 100% ✅
  - 0 should be 0% ✅
  - 1 should be 1 ✅
  - 1.33 should be 1.33 ✅


- Friend page
  - Show all his games ✅
  - Show match points, show group points ✅
  - Show top scorer points ✅
  - Show stage in games tables ✅
  - Add link to match ✅
  - Add link to stage ✅
  - Show statistics
    - Avg points per match, amount of hits/bullseye


- Standings page
  - Show all total points per player ✅
  - Added ranking
    - two players with equal points should be the same rank ✅

- Save points automatically
  - Hard coded points ✅
  - By rules in the DB ✅

- Tofes
  - Create predictions for a friend when he is created
    - for that a user should register to a tournament ✅
    - delete when unregistering a user ✅
  - Create predictions for all friends when a match is created



