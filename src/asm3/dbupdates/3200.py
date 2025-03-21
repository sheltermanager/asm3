# Add the trial adoption fields to the adoption table
add_column(dbo, "adoption", "IsTrial", "INTEGER")
add_column(dbo, "adoption", "TrialEndDate", dbo.type_datetime)
add_index(dbo, "adoption_TrialEndDate", "adoption", "TrialEndDate")