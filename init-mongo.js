db.createUser(
    {
        user: "embedding",
            pwd: "embedding_password",
            roles: [
            {
                role: "readWrite",
                db: "athene_db"
            }
        ]
    }
);
db.createUser(
    {
        user: "clustering",
        pwd: "clustering_password",
        roles: [
            {
                role: "readWrite",
                db: "athene_db"
            }
        ]
    }
);
