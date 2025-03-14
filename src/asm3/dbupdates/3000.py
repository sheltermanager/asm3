path = dbo.installpath
asm2_dbfs_put_file(dbo, "adoption_form.html", "/templates", path + "media/templates/adoption_form.html")
asm2_dbfs_put_file(dbo, "cat_assessment_form.html", "/templates", path + "media/templates/cat_assessment_form.html")
asm2_dbfs_put_file(dbo, "cat_cage_card.html", "/templates", path + "media/templates/cat_cage_card.html")
asm2_dbfs_put_file(dbo, "cat_information.html", "/templates", path + "media/templates/cat_information.html")
asm2_dbfs_put_file(dbo, "dog_assessment_form.html", "/templates", path + "media/templates/dog_assessment_form.html")
asm2_dbfs_put_file(dbo, "dog_cage_card.html", "/templates", path + "media/templates/dog_cage_card.html")
asm2_dbfs_put_file(dbo, "dog_information.html", "/templates", path + "media/templates/dog_information.html")
asm2_dbfs_put_file(dbo, "dog_license.html", "/templates", path + "media/templates/dog_license.html")
asm2_dbfs_put_file(dbo, "fancy_cage_card.html", "/templates", path + "media/templates/fancy_cage_card.html")
asm2_dbfs_put_file(dbo, "half_a4_cage_card.html", "/templates", path + "media/templates/half_a4_cage_card.html")
asm2_dbfs_put_file(dbo, "homecheck_form.html", "/templates", path + "media/templates/homecheck_form.html")
asm2_dbfs_put_file(dbo, "invoice.html", "/templates", path + "media/templates/invoice.html")
asm2_dbfs_put_file(dbo, "microchip_form.html", "/templates", path + "media/templates/microchip_form.html")
asm2_dbfs_put_file(dbo, "petplan.html", "/templates", path + "media/templates/petplan.html")
asm2_dbfs_put_file(dbo, "rabies_certificate.html", "/templates", path + "media/templates/rabies_certificate.html")
asm2_dbfs_put_file(dbo, "receipt.html", "/templates", path + "media/templates/receipt.html")
asm2_dbfs_put_file(dbo, "receipt_tax.html", "/templates", path + "media/templates/receipt_tax.html")
asm2_dbfs_put_file(dbo, "reserved.html", "/templates", path + "media/templates/reserved.html")
asm2_dbfs_put_file(dbo, "spay_neuter_voucher.html", "/templates", path + "media/templates/spay_neuter_voucher.html")
asm2_dbfs_put_file(dbo, "rspca_adoption.html", "/templates/rspca", path + "media/templates/rspca/rspca_adoption.html")
asm2_dbfs_put_file(dbo, "rspca_behaviour_observations_cat.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_cat.html")
asm2_dbfs_put_file(dbo, "rspca_behaviour_observations_dog.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_dog.html")
asm2_dbfs_put_file(dbo, "rspca_behaviour_observations_rabbit.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_rabbit.html")
asm2_dbfs_put_file(dbo, "rspca_dog_advice_leaflet.html", "/templates/rspca", path + "media/templates/rspca/rspca_dog_advice_leaflet.html")
asm2_dbfs_put_file(dbo, "rspca_post_home_visit.html", "/templates/rspca", path + "media/templates/rspca/rspca_post_home_visit.html")
asm2_dbfs_put_file(dbo, "rspca_transfer_of_ownership.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_ownership.html")
asm2_dbfs_put_file(dbo, "rspca_transfer_of_title.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_title.html")
asm2_dbfs_put_file(dbo, "nopic.jpg", "/reports", path + "media/reports/nopic.jpg")
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Added", dbo.type_datetime, False),
    dbo.ddl_add_table_column("Expires", dbo.type_datetime, False),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Priority", dbo.type_integer, False),
    dbo.ddl_add_table_column("Message", dbo.type_longtext, False)
])
dbo.execute_dbupdate( dbo.ddl_add_table("messages", fields) )
add_index(dbo, "messages_Expires", "messages", "Expires")
