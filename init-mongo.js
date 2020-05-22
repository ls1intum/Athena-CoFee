db.createUser(
    {
        user: "user1",
        pwd: "user1_password",
        roles: [
            {
                role: "readWrite",
                db: "athene_db"
            }
        ]
    }
)
