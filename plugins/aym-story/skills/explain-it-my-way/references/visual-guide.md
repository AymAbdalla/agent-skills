# Visual guide

Read this while making an explanation visual. Choose the smallest form that makes the idea understandable.

## Show a concrete situation

Keep one example throughout. A flow about saving a task should show that task going through the system, rather than switching to a restaurant analogy, a payment example, and a generic architecture drawing in the same explanation.

Use recognizable roles and outcomes: "your phone," "save request," "saved task," "reply went missing." Introduce precise technical labels after these roles make sense. A second vocabulary view may replace or pair the labels without changing the underlying example.

Prefer roughly three to seven main visual parts. Split a larger system into an overview and focused detail. Put explanations beside the diagram instead of cramming sentences into boxes. Label arrows with what moves or what causes the next event.

## Pick the right visual

| Understanding needed | Useful form | Show explicitly |
| --- | --- | --- |
| Order of steps | Flow or sequence | Starting event, direction, result |
| Parts and responsibilities | Labeled structure | Who does what and where data lives |
| Why an approach helps | Before/after illustration | Same starting conditions and changed outcome |
| A failure or recovery | Small story in panels | Failure point, recovery action, remaining limit |
| Changing inputs or rules | Interactive example | User control, changed state, visible consequence |
| Options and tradeoffs | Side-by-side comparison | Equal assumptions and material differences |

For a single definition, a small concrete example can do more than a diagram. Avoid a decorative image that adds no understanding. Use image generation when a conceptual illustration helps and the available tool and any spending are authorized. Put exact labels in editable markup rather than relying on generated image text. A generated conceptual picture is not evidence of actual product behavior.

## Make it readable

- Use large text, short labels, clear spacing, and a small set of consistent colors.
- Use text or shapes as well as color to explain state. Check contrast and small-screen wrapping.
- Explain numbers and axes; identify teaching numbers as examples.
- Provide an adjacent text explanation or useful image description.
- Show both plain and technical labels only when they fit. Otherwise use separate views.
- Label simulated examples as simulated. Do not imply a browser demo exercises the real app, network, database, or payment system.

## Interaction should teach

Use interaction when it lets the reader see cause and effect. For example, allow a lost reply and a retry, then show whether a second task appears. Give the reader a clear first action, keep the state visible, and offer a reset. A toggle that only hides text is presentation, not a working model of the system.

Keep controls keyboard accessible. Respect reduced-motion settings when using animation. Avoid network dependencies when a standalone HTML/SVG example can teach the idea locally. Keep explanatory content readable with scripts unavailable when practical.

## Render and preserve source

Prefer the available inline visualization tool for an interactive explanation. For a saved example, a self-contained HTML file with inline SVG can provide both interaction and editable source. For a small static flow, rendered Mermaid is suitable when the viewer supports it. A raw Mermaid code fence is source, not proof that rendering succeeded.

Use an existing diagram tool when it fits. Check its actual output: a diagram inside an Excalidraw file may be separate editable shapes or a single embedded image. Describe the editability you verified, rather than assuming a file extension proves it.

Preserve `.html`, `.svg`, `.mmd`, or a scene file as appropriate. "Editable source" means the content can be changed in its source file. "Editable shapes" means a visual editor can change individual diagram objects. Do not conflate these claims.

If saving an artifact, inspect the rendered result with an available browser or viewer. For an interactive model, exercise its main controls and check that the observed results agree with the explanation. For example, test the retry and reset, not just page loading. When inspection is unavailable, name that limitation and deliver readable text plus the best available source or fallback.

## Do not smooth over an important limit

An analogy may show a ticket number being checked once; a real system may also need to handle two requests arriving together. Show or explain the limit when it matters to the professional comparison. "Our demo shows the rule" and "our real implementation handles this failure" require different evidence.

Finish by pointing at the visual: tell the reader what changed, what stayed the same, and what decision that helps them make.
