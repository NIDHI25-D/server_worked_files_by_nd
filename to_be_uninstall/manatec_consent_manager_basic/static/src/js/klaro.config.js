window.klaroConfig = {
    privacyPolicy: window.klaroDefault.privacyPolicy,
    cookieDomain: window.klaroDefault.domain,
    apps : [
        {
            name : 'google-analytics',
            default: true,
            title : 'Google Analytics',
            purposes: ['statistics'],
            cookies : [
                [/^_ga/i, window.klaroDefault.domainPath, window.klaroDefault.domain],
                [/^_gat/i, window.klaroDefault.domainPath, window.klaroDefault.domain],
                [/^_gid/i, window.klaroDefault.domainPath, window.klaroDefault.domain],
            ],
        },
        {
            name : 'essential',
            default: true,
            required: true,
            title : 'Essential',
            purposes: ['essential'],
        },
    ],
    translations: {
        // If you erase the "consentModal" translations, Klaro will use the
        // bundled translations.
        de: {
            consentModal: {
                description:
                    "Wir nutzen Cookies auf unserer Website. Einige von ihnen sind essenziell, während andere uns helfen, diese Website und Ihre Erfahrung zu verbessern.",
            },
            consentNotice: {
                learnMore: "Einstellungen",
            },
            'google-analytics': {
                description: 'Google Analytics ist ein Trackingtool zur Datenverkehrsanalyse von Webseiten. Wir nutzen Google Analytics, um das Nutzerverhalten der Besucher unserer Website zu verstehen und die allgemeine User-Experience zu verbessern.',
            },
            'essential': {
                description: 'Essentials dienen der Funktionalität der Website. Wir nutzen Essential-Cookies zur generellen Funktionalität und zur Navigation auf der Website.',
            },
            purposes: {
                statistics: 'Besucher Statistiken',
                essential: 'Essentiell',
            },
            ok: "Akzeptieren",
            acceptSelected: "Auswahl akzeptieren"
        },
        en: {
            consentModal: {
                description:
                    "We use cookies and similar technologies. Some cookies are essential for this websites functionality, some help us to understand how you use our site and to improve your experience.",
            },
            consentNotice: {
                learnMore: "Settings",
            },
            'google-analytics': {
                description: 'Google Analytics is a tracking tool for traffic analysis of websites. We use Google Analytics to understand the user behaviour of visitors to our website and to improve the general user experience.',
            },
            'essential': {
                description: 'Essentials serve the functionality of the website. We use Essential cookies for general functionality and navigation on the site.',
            },
            purposes: {
                statistics: 'Visitor Statistics',
                essential: 'Essential'
            }
        }
    }
};
