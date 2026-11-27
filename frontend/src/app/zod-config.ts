import { z } from "zod"

// Zod probes `new Function` each time it builds an object schema. The
// Content-Security-Policy forbids eval and the browser reports that probe as a
// violation even though Zod catches it, so turn the JIT fast path off.
z.config({ jitless: true })
