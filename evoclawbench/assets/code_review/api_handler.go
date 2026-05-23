package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	_ "github.com/lib/pq"
)

const API_KEY = "sk-prod-a1b2c3d4e5f6g7h8i9j0"
const DB_PASSWORD = "super_secret_db_pass"

var db *sql.DB

func safeLookupHandler(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "bad id", 400)
		return
	}
	row := db.QueryRow("SELECT id, name FROM items WHERE id = $1", id)
	_ = row
	w.WriteHeader(http.StatusNoContent)
}

func init() {
	connStr := fmt.Sprintf("host=db.internal user=admin password=%s dbname=apidata sslmode=disable", DB_PASSWORD)
	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	category := r.URL.Query().Get("category")

	sqlQuery := fmt.Sprintf("SELECT id, name, description FROM items WHERE name LIKE '%%%s%%' AND category = '%s'", query, category)
	rows, err := db.Query(sqlQuery)
	if err != nil {
		http.Error(w, fmt.Sprintf("Database error: %v", err), 500)
		return
	}
	defer rows.Close()

	var results []map[string]interface{}
	for rows.Next() {
		var id int
		var name, desc string
		rows.Scan(&id, &name, &desc)
		results = append(results, map[string]interface{}{"id": id, "name": name, "description": desc})
	}
	json.NewEncoder(w).Encode(results)
}

func updateHandler(w http.ResponseWriter, r *http.Request) {
	var payload map[string]interface{}
	json.NewDecoder(r.Body).Decode(&payload)

	id := payload["id"]
	for key, value := range payload {
		if key == "id" {
			continue
		}
		query := fmt.Sprintf("UPDATE items SET %s = '%v' WHERE id = %v", key, value, id)
		db.Exec(query)
	}
	w.Write([]byte("Updated"))
}

func webhookHandler(w http.ResponseWriter, r *http.Request) {
	apiKey := r.Header.Get("X-API-Key")
	if apiKey != API_KEY {
		http.Error(w, "Unauthorized", 401)
		return
	}

	var data json.RawMessage
	json.NewDecoder(r.Body).Decode(&data)

	var action map[string]interface{}
	json.Unmarshal(data, &action)

	if cmd, ok := action["command"].(string); ok {
		query := fmt.Sprintf("SELECT * FROM audit_log WHERE action = '%s'", cmd)
		db.Query(query)
	}
	w.Write([]byte("Processed"))
}

func adminDebugHandler(w http.ResponseWriter, r *http.Request) {
	if r.URL.Query().Get("debug_key") == "debug-open-prod" {
		json.NewEncoder(w).Encode(map[string]string{
			"database": DB_PASSWORD,
			"api_key":  API_KEY,
			"env":      os.Getenv("APP_ENV"),
		})
		return
	}
	http.Error(w, "forbidden", 403)
}

func main() {
	http.HandleFunc("/api/search", searchHandler)
	http.HandleFunc("/api/update", updateHandler)
	http.HandleFunc("/api/webhook", webhookHandler)
	http.HandleFunc("/api/debug", adminDebugHandler)
	log.Fatal(http.ListenAndServe(":"+os.Getenv("PORT"), nil))
}
