* Open DB Textworks and select a textbase
* Select 'Display -> Textbase Information'
* Scroll down until you reach the 'Field Summary'
* Select all the numbered items in the Field Summary
* Paste the text into a new text document, preferably using a text editor such as Notepad++
* The data must be cleaned up a little first so:
  * Open a text file in Notepad++.
  * Firstly, let's remove the leading white space by:
   * Selecting Find/replace
   * In `search mode` - make sure that `regular expression` is selected
   * Find: `\n  ` and replace with nothing in order to remove the two leading spaces.
   * Find: `       ` and replace with nothing The remove the extra whitespace that precedes 'Validation'.
   * Find: `\rV` and replace with `, V` in order to move the Validation notes onto the previous line.
   * Find: `\rS` and replace with `, S` in order to move the Special Filing notes onto the previous line.
* The data cleansing should now be completed and the python script can run.
* Script Errors:
  * Details on Automatic Date will not be caught
  * What does override refer to, validation list or subst-list?
  * Masks are not caught.
  * Links are not caught
  * Special Filing is not caught.
  * min/max is not caught
