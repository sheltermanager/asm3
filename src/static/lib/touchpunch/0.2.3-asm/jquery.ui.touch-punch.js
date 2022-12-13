/*!
 * jQuery UI Touch Punch 0.2.3-asm
 *
 * Copyright 2011–2014, Dave Furfero
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * Modified 13/12/2022 R Rawson-Tetley to fall back to pointer events 
 * if touch events are not available. This was done because some customers have
 * touchscreen Lenovo monitors with styluses that do not generate touch events,
 * but they do generate pointer events. 
 *
 * Depends:
 *  jquery.ui.widget.js
 *  jquery.ui.mouse.js
 */
(function ($) {

  // Detect touch and pointer support
  $.support.touch = 'ontouchend' in document;
  $.support.pointer = 'onpointerdown' in document;

  // Ignore browsers without touch or pointer support
  if (!$.support.touch && !$.support.pointer) {
    return;
  }

  var mouseProto = $.ui.mouse.prototype,
      _mouseInit = mouseProto._mouseInit,
      _mouseDestroy = mouseProto._mouseDestroy,
      touchHandled;

  /**
   * Simulate a mouse event based on a corresponding touch event
   * @param {Object} event A touch event
   * @param {String} simulatedType The corresponding mouse event
   */
  function simulateMouseEvent (event, simulatedType) {

    event.preventDefault();

    // Pointer event attributes are on the actual event, where touch are in changedTouches
    var touch;
    if ($.support.touch) { touch = event.originalEvent.changedTouches[0]; } else if ($.support.pointer) { touch = event.originalEvent; } 

    var simulatedEvent = document.createEvent('MouseEvents');
    
    // Initialize the simulated mouse event using the touch event's coordinates
    simulatedEvent.initMouseEvent(
      simulatedType,    // type
      true,             // bubbles                    
      true,             // cancelable                 
      window,           // view                       
      1,                // detail                     
      touch.screenX,    // screenX                    
      touch.screenY,    // screenY                    
      touch.clientX,    // clientX                    
      touch.clientY,    // clientY                    
      false,            // ctrlKey                    
      false,            // altKey                     
      false,            // shiftKey                   
      false,            // metaKey                    
      0,                // button                     
      null              // relatedTarget              
    );

    // Dispatch the simulated event to the target element
    event.target.dispatchEvent(simulatedEvent);
  }

  /**
   * Handle the jQuery UI widget's touchstart events
   * @param {Object} event The widget element's touchstart event
   */
  mouseProto._touchStart = function (event) {

    var self = this;

    // Ignore the event if another widget is already being handled
    if (touchHandled) {
      return;
    }

    // Set the flag to prevent other widgets from inheriting the touch event
    touchHandled = true;

    // Track movement to determine if interaction was a click
    self._touchMoved = false;

    // Simulate the mouseover event
    simulateMouseEvent(event, 'mouseover');

    // Simulate the mousemove event
    simulateMouseEvent(event, 'mousemove');

    // Simulate the mousedown event
    simulateMouseEvent(event, 'mousedown');
  };

  /**
   * Handle the jQuery UI widget's touchmove events
   * @param {Object} event The document's touchmove event
   */
  mouseProto._touchMove = function (event) {

    // Ignore event if not handled
    if (!touchHandled) {
      return;
    }

    // Interaction was not a click
    this._touchMoved = true;

    // Simulate the mousemove event
    simulateMouseEvent(event, 'mousemove');
  };

  /**
   * Handle the jQuery UI widget's touchend events
   * @param {Object} event The document's touchend event
   */
  mouseProto._touchEnd = function (event) {

    // Ignore event if not handled
    if (!touchHandled) {
      return;
    }

    // Simulate the mouseup event
    simulateMouseEvent(event, 'mouseup');

    // Simulate the mouseout event
    simulateMouseEvent(event, 'mouseout');

    // If the touch interaction did not move, it should trigger a click
    if (!this._touchMoved) {

      // Simulate the click event
      simulateMouseEvent(event, 'click');
    }

    // Unset the flag to allow other widgets to inherit the touch event
    touchHandled = false;
  };

  /**
   * A duck punch of the $.ui.mouse _mouseInit method to support touch events.
   * This method extends the widget with bound touch event handlers that
   * translate touch events to mouse events and pass them to the widget's
   * original mouse event handling methods.
   */
  mouseProto._mouseInit = function () {
    
    var self = this;

    // Delegate the pointer/touch handlers to the widget's element
    if ($.support.touch) {
        self.element.bind({
          touchstart: $.proxy(self, '_touchStart'),
          touchmove: $.proxy(self, '_touchMove'),
          touchend: $.proxy(self, '_touchEnd')
        });
    }
   else if ($.support.pointer) {
        self.element.bind({
          pointerdown: $.proxy(self, '_touchStart'),
          pointermove: $.proxy(self, '_touchMove'),
          pointerup: $.proxy(self, '_touchEnd')
        });
    }


    // Call the original $.ui.mouse init method
    _mouseInit.call(self);
  };

  /**
   * Remove the touch event handlers
   */
  mouseProto._mouseDestroy = function () {
    
    var self = this;

    // Delegate the touch handlers to the widget's element
    if ($.support.touch) {
        self.element.unbind({
          touchstart: $.proxy(self, '_touchStart'),
          touchmove: $.proxy(self, '_touchMove'),
          touchend: $.proxy(self, '_touchEnd')
        });
    }
   else if ($.support.pointer) {
        self.element.unbind({
          pointerdown: $.proxy(self, '_touchStart'),
          pointermove: $.proxy(self, '_touchMove'),
          pointerup: $.proxy(self, '_touchEnd')
        });
    }

    // Call the original $.ui.mouse destroy method
    _mouseDestroy.call(self);
  };

})(jQuery);
