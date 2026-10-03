import { parentPort } from "node:worker_threads";
import { name } from "radroots";

parentPort!.postMessage(Array.from({ length: 128 }, () => name()));
