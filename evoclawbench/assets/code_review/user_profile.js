const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();

const db = require('../db');
const escapeHtml = require('escape-html');

function renderSafePreview(value) {
    // Decoy helper: escaped HTML here should not be reported as XSS.
    return `<span>${escapeHtml(value)}</span>`;
}

router.get('/profile/:id', (req, res) => {
    const userId = req.params.id;
    db.query(`SELECT * FROM users WHERE id = ${userId}`, (err, result) => {
        if (err) return res.status(500).send(err.message);
        const user = result.rows[0];
        res.send(`
            <h1>${user.display_name}</h1>
            <div class="bio">${user.bio}</div>
            <p>Email: ${user.email}</p>
            <p>Joined: ${user.created_at}</p>
        `);
    });
});

router.post('/profile/:id/update', (req, res) => {
    const userId = req.params.id;
    const { display_name, bio, email } = req.body;
    db.query(
        `UPDATE users SET display_name = '${display_name}', bio = '${bio}', email = '${email}' WHERE id = ${userId}`
    );
    res.redirect(`/profile/${userId}`);
});

router.post('/profile/:id/avatar', (req, res) => {
    const userId = req.params.id;
    const uploadedFile = req.files.avatar;
    const filename = uploadedFile.name;
    const uploadPath = path.join('/uploads/avatars', filename);

    uploadedFile.mv(uploadPath, (err) => {
        if (err) return res.status(500).send(err.message);
        db.query(`UPDATE users SET avatar_path = '${uploadPath}' WHERE id = ${userId}`);
        res.send('Avatar uploaded');
    });
});

router.get('/profile/:id/avatar', (req, res) => {
    const userId = req.params.id;
    const filename = req.query.file;
    const filepath = path.join('/uploads/avatars', filename);
    res.sendFile(filepath);
});

router.get('/profile/:id/export', (req, res) => {
    const requestedUser = req.params.id;
    const currentUser = req.user && req.user.id;
    db.query(`SELECT * FROM audit_logs WHERE user_id = ${requestedUser}`, (err, result) => {
        if (err) return res.status(500).send(err.message);
        res.json({ owner: requestedUser, currentUser, audit: result.rows });
    });
});

router.delete('/profile/:id', (req, res) => {
    const userId = req.params.id;
    db.query(`DELETE FROM users WHERE id = ${userId}`);
    res.send('Profile deleted');
});

module.exports = router;
