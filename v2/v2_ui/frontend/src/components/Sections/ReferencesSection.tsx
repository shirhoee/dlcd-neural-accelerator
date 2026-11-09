import React from 'react';
import styles from './ReferencesSection.module.css';
import { BookOpen, ExternalLink } from 'lucide-react';

interface ReferenceItem {
  id: number;
  authors: string;
  year: string;
  title: string;
  publication: string;
  doiOrUrl?: string;
}

const REFERENCES: ReferenceItem[] = [
  {
    id: 1,
    authors: 'Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner',
    year: '1998',
    title: 'Gradient-based learning applied to document recognition',
    publication: 'Proceedings of the IEEE, vol. 86, no. 11, pp. 2278-2324',
    doiOrUrl: 'https://doi.org/10.1109/5.726791',
  },
  {
    id: 2,
    authors: 'H. T. Kung',
    year: '1982',
    title: 'Why systolic architectures?',
    publication: 'IEEE Computer, vol. 15, no. 1, pp. 37-46',
    doiOrUrl: 'https://doi.org/10.1109/MC.1982.1653825',
  },
  {
    id: 3,
    authors: 'N. P. Jouppi et al.',
    year: '2017',
    title: 'In-datacenter performance analysis of a tensor processing unit',
    publication: 'ACM/IEEE 44th Annual International Symposium on Computer Architecture (ISCA), pp. 1-12',
    doiOrUrl: 'https://doi.org/10.1145/3079856.3080246',
  },
  {
    id: 4,
    authors: 'IEEE Computer Society',
    year: '2001',
    title: 'IEEE Standard for Verilog Hardware Description Language',
    publication: 'IEEE Std 1364-2001 (Revision of IEEE Std 1364-1995), pp. 1-792',
    doiOrUrl: 'https://ieeexplore.ieee.org/document/954933',
  },
  {
    id: 5,
    authors: 'Dept. of Computer Science & Engineering, PES University',
    year: '2026',
    title: 'UE25CS251A Digital Logic and Computer Design Laboratory Lab Manual',
    publication: 'End Semester Assessment (ESA) Project Framework, Ring Road Campus, Bengaluru',
  },
];

export const ReferencesSection: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.tag}>SECTION 8 &bull; BIBLIOGRAPHY</div>
        <h2 className={styles.title}>Academic &amp; Architectural References</h2>
        <p className={styles.desc}>
          Foundational research in systolic computing arrays, fixed-point convolution pipelines, and IEEE 1364-2001 hardware description standards.
        </p>
      </div>

      <div className={styles.refsList}>
        {REFERENCES.map((ref) => (
          <div key={ref.id} className={styles.refCard}>
            <div className={styles.refNumber}>[{ref.id}]</div>
            <div className={styles.refBody}>
              <div className={styles.refAuthors}>
                {ref.authors} ({ref.year}).
              </div>
              <div className={styles.refTitle}>"{ref.title}."</div>
              <div className={styles.refPub}>{ref.publication}.</div>
              {ref.doiOrUrl && (
                <a
                  href={ref.doiOrUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.refLink}
                >
                  <BookOpen size={12} />
                  <span>{ref.doiOrUrl}</span>
                  <ExternalLink size={11} />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
