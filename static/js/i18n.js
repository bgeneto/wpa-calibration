const lngs = {
  en: { nativeName: 'English' },
  es: { nativeName: 'Español' },
  pt: { nativeName: 'Português' }
};

const rerender = () => {
  // start localizing, details:
  // https://github.com/i18next/jquery-i18next#usage-of-selector-function
  $('body').localize();
  $('title').text($.t('head.title'))
  $('meta[name=description]').attr('content', $.t('head.description'))
}

$(function () {
  // use plugins and options as needed, for options, detail see
  // https://www.i18next.com
  i18next
    // detect user language
    // learn more: https://github.com/i18next/i18next-browser-languageDetector
    .use(i18nextBrowserLanguageDetector)
    // init i18next
    // for all options read: https://www.i18next.com/overview/configuration-options
    .init({
      debug: true,
      fallbackLng: 'en',
      resources: {
        en: {
          translation: {
            head: {
              title: 'Pendulum Calibration Tool',
              description: 'Web interface for Pendulum Calibration Tool.'
            },
            intro: {
              title: 'Pendulum Calibration Tool',
              subtitle: 'Use this page to configure pendulum initial parameters'
            },
            promo: {
              title: 'Warning',
              text: 'No warnings today'
            },
            data: {
              output: 'Pendulum data output',
              input: 'Pendulum data input',
              output_label: 'Serial port output',
              button: 'Clear'
            },
            command: {
              label: 'Send Command',
              placeholder: 'Type your command here...',
              button: 'Send'
            },
            menu: {
              pages: 'Pages',
              index: 'Serial Port I/O',
              cal1: 'Calibration 1',
              cal2: 'Calibration 2'
            },
            cal: {
              title1: 'Pendulum Calibration (step 1)',
              id_string: 'Pendulum Name',
              max_pos: 'Maximum position',
              vert_pos: 'Vertical position',
              diameter: 'Sphere diameter',
              pulley: 'Pulley diameter',
              length: 'Pendulum length',
              origin: 'Origin position',
              photodiode: 'Photodiode position'
            }
          }
        },
        pt: {
          translation: {
            head: {
              title: 'Ferramenta para Calibração do Pêndulo',
              description: 'Interface web para Ferramenta para Calibração do Pêndulo.'
            },
            intro: {
              title: 'Ferramenta para Calibração do Pêndulo',
              subtitle: 'Utilize esta página para configurar os parâmetros do pêndulo'
            },
            promo: {
              title: 'Aviso',
              text: 'Estamos 0 dias sem acidentes'
            },
            data: {
              output: 'Saída de dados do pêndulo',
              input: 'Entrada de dados do pêndulo',
              output_label: 'Saída da porta serial',
              button: 'Limpar'
            },
            command: {
              label: 'Enviar Comando',
              placeholder: 'Digite seu comando aqui...',
              button: 'Enviar'
            },
            menu: {
              pages: 'Páginas',
              index: 'Porta Serial E/S',
              cal1: 'Calibração 1',
              cal2: 'Calibração 2'
            },
            cal: {
              title1: 'Calibração do Pêndulo (passo 1)',
              id_string: 'Nome do pêndulo',
              max_pos: 'Posição máxima',
              vert_pos: 'Posição vertical',
              diameter: 'Diâmetro da esfera',
              pulley: 'Pulley diameter',
              length: 'Comprimento do pêndulo',
              origin: 'Posição na origem',
              photodiode: 'Posição do fotodiodo'
            }
          }
        }
      }
    }, (err, t) => {
      if (err) return console.error(err);

      // for options see
      // https://github.com/i18next/jquery-i18next#initialize-the-plugin
      jqueryI18next.init(i18next, $, { useOptionsAttr: true });

      // fill language switcher
      Object.keys(lngs).map((lng) => {
        const opt = new Option(lngs[lng].nativeName, lng);
        if (lng === i18next.resolvedLanguage) {
          opt.setAttribute("selected", "selected");
        }
        $('#languageSwitcher').append(opt);
      });
      $('#languageSwitcher').change((a, b, c) => {
        const chosenLng = $(this).find("option:selected").attr('value');
        i18next.changeLanguage(chosenLng, () => {
          rerender();
        });
      });

      rerender();
    });
});