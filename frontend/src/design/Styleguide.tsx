import { PageHeading, Section } from '../ui';

export default function Styleguide() {
  return <><PageHeading eyebrow="Design checkpoint" title="A visual language for careful reading" intro="Neutral surfaces keep attention on the evidence. Warm and cool hues carry lighting data only when a measured value exists." />
    <Section title="Type and measure"><p>This reading column uses Source Serif 4 for prose. Controls, tables and figure labels use Public Sans. Numerals align for comparison.</p><p className="small-text">Secondary text remains readable in both themes. Every data mark needs a label, caption, and accessible text alternative.</p></Section>
    <Section title="Figure palette"><div className="swatches"><div className="swatch"><i style={{ background: 'var(--lamp)' }} />Warm illuminant</div><div className="swatch"><i style={{ background: 'var(--sky)' }} />Cool illuminant</div><div className="swatch"><i style={{ background: 'var(--alert)' }} />Invalid or excluded</div></div></Section>
    <Section title="Controls"><div className="toolbar"><button>Primary action</button><button className="subtle">Secondary action</button><label>Experiment <select><option>All experiments</option><option>Experiment 1</option></select></label></div></Section></>;
}
