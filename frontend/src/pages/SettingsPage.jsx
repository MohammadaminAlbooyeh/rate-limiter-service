import React from 'react';

function SettingsPage() {
  return (
    <div>
      <h1>Settings</h1>
      <form>
        <label>Redis Host: <input type="text" /></label>
        <label>Redis Port: <input type="number" /></label>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}

export default SettingsPage;
