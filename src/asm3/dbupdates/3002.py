add_column(dbo, "users", "IPRestriction", dbo.type_longtext)
execute(dbo,"CREATE TABLE role (ID INTEGER NOT NULL PRIMARY KEY, " \
    "Rolename %s NOT NULL, SecurityMap %s NOT NULL)" % (dbo.type_shorttext, dbo.type_longtext))
add_index(dbo, "role_Rolename", "role", "Rolename")
execute(dbo,"CREATE TABLE userrole (UserID INTEGER NOT NULL, " \
    "RoleID INTEGER NOT NULL)")
add_index(dbo, "userrole_UserIDRoleID", "userrole", "UserID, RoleID")
# Create default roles
execute(dbo,"INSERT INTO role VALUES (1, 'Other Organisation', 'va *vavet *vav *mvam *dvad *cvad *vamv *vo *volk *vle *vvov *vdn *vla *vfa *vwl *vcr *vll *')")
execute(dbo,"INSERT INTO role VALUES (2, 'Staff', 'aa *ca *va *vavet *da *cloa *gaf *aam *cam *dam *vam *mand *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad *caad *cdad *cvad *aamv *camv *vamv *damv *ao *co *vo *do *mo *volk *ale *cle *dle *vle *vaov *vcov *vvov *oaod *ocod *odod *ovod *vdn *edt *adn *eadn *emdn *ecdn *bcn *ddn *pdn *pvd *ala *cla *dla *vla *afa *cfa *dfa *vfa *mlaf *vwl *awl *cwl *dwl *bcwl *all *cll *vll *dll *vcr *')")
execute(dbo,"INSERT INTO role VALUES (3, 'Accountant', 'aac *vac *cac *ctrx *dac *vaov *vcov *vdov *vvov *oaod *ocod *odod *ovod *')")
execute(dbo,"INSERT INTO role VALUES (4, 'Vet', 'va *vavet *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad * ')")
execute(dbo,"INSERT INTO role VALUES (5, 'Publisher', 'uipb *')")
execute(dbo,"INSERT INTO role VALUES (6, 'System Admin', 'asm *cso *ml *usi *rdbu *rdbd *asu *esu *ccr *vcr *hcr *dcr *')")
execute(dbo,"INSERT INTO role VALUES (7, 'Marketer', 'uipb *mmeo *mmea *')")
execute(dbo,"INSERT INTO role VALUES (8, 'Investigator', 'aoi *coi *doi *voi *')")
# Find any existing users that aren't superusers and create a
# matching role for them
users = dbo.query("SELECT ID, UserName, SecurityMap FROM users " \
    "WHERE SuperUser = 0")
for u in users:
    roleid = dbo.get_id_max("role") 
    # If it's the guest user, use the view animals/people role
    if u["USERNAME"] == "guest":
        roleid = 1
    else:
        execute(dbo,"INSERT INTO role VALUES (%d, '%s', '%s')" % \
            ( roleid, u["USERNAME"], u["SECURITYMAP"]))
    execute(dbo,"INSERT INTO userrole VALUES (%d, %d)" % \
        ( u["ID"], roleid))
