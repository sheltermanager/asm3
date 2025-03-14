# Add the has trial adoption denormalised field to the animal table and update it
add_column(dbo, "animal", "HasTrialAdoption", "INTEGER")
execute(dbo,"UPDATE animal SET HasTrialAdoption = 0")
execute(dbo,"UPDATE adoption SET IsTrial = 0 WHERE IsTrial Is Null")