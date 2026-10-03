import { NAME, name, printName } from "radroots";
import {
  initialize,
  name as browserName,
  printName as browserPrint,
} from "radroots/browser";

const label: string = NAME;
const value: string = name();
const print: () => void = printName;
const browserValue: () => string = browserName;
const browserPrinter: () => void = browserPrint;
const start: typeof initialize = initialize;

void [label, value, print, browserValue, browserPrinter, start];
