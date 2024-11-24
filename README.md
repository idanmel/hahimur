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

  
- Match predictions
  - See a blank page with no predictions ✅
  - See one friend's prediction ✅
  - See multiple friend predictions ✅
  - If the game is not scored yet, show zero points ✅
  - If the game is scored, show the score for each prediction ✅
  - Default order by points ✅
  - User can change order ✅
  - Statistics
    - How many friends participated, guessed, hit



- Stage points
  - very similar to the match predictions ✅
  - Show Matches ✅
  - Show Group Table 


- Match stats ✅
  - Results: Bullseye, Hit, Wrong, Didn't play ✅
  - If match didn't start yet, let's not do it. ✅
  - 1/3 should be 33.33% ✅
  - 1 should be 100% ✅
  - 0 should be 0% ✅