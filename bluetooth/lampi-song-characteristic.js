var util = require('util');
var bleno = require('bleno');

var CHARACTERISTIC_NAME = 'Song Name';

function LampiSongCharacteristic(lampiState) {
  LampiSongCharacteristic.super_.call(this, {
    uuid: '0005A7D3-D8A4-4FEA-8174-1736E808C066',
    properties: ['read', 'write', 'notify'],
    secure: [],
    descriptors: [
        new bleno.Descriptor({
            uuid: '2901',
            value: CHARACTERISTIC_NAME,
        }),
        new bleno.Descriptor({
           uuid: '2904',
           value: new Buffer([0x07, 0x00, 0x27, 0x00, 0x01, 0x00, 0x00])
        }),
    ],
  });

  this._update = null;

  this.changed_song =  function(song) {
    if( this._update !== null ) {
        var data = new Buffer(song);
        this._update(data);
    } 
  }

  this.lampiState = lampiState;

  this.lampiState.on('changed-song', this.changed_song.bind(this));

}

util.inherits(LampiSongCharacteristic, bleno.Characteristic);

LampiSongCharacteristic.prototype.onReadRequest = function(offset, callback) {
  console.log('onReadRequest');
  if (offset) {
    console.log('onReadRequest offset');
    callback(this.RESULT_ATTR_NOT_LONG, null);
  }
  else {
    var data = new Buffer("Ghost Town By Kanye West");
    console.log('onReadRequest returning ', data);
    callback(this.RESULT_SUCCESS, data);
  }
};

LampiSongCharacteristic.prototype.onWriteRequest = function(data, offset, withoutResponse, callback) {
    console.log('onWriteRequest');
    if(offset) {
        callback(this.RESULT_ATTR_NOT_LONG);
    }
    else {
        var song = data.toString();
        this.lampiState.set_song( song );
        callback(this.RESULT_SUCCESS);
    }
};

LampiSongCharacteristic.prototype.onSubscribe = function(maxValueSize, updateValueCallback) {
    console.log('subscribe on ', CHARACTERISTIC_NAME);
    this._update = updateValueCallback;
}

LampiSongCharacteristic.prototype.onUnsubscribe = function() {
    console.log('unsubscribe on ', CHARACTERISTIC_NAME);
    this._update = null;
}

module.exports = LampiSongCharacteristic;
