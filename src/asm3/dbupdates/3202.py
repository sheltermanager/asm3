# Set default value for HasTrialAdoption
execute(dbo,"UPDATE animal SET HasTrialAdoption = 1 WHERE EXISTS(SELECT ID FROM adoption ad WHERE ad.IsTrial = 1 AND ad.AnimalID = animal.ID)")
