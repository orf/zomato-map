import React, { Component } from 'react';
import './App.css';
import places from './places.json';

class App extends Component {
  render() {
    return (
      <div>Places: {places.places.length}</div>
    );
  }
}

export default App;
