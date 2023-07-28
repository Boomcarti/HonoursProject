from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:aizen@localhost:3306/lexdb'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class PhoneticEnvironment(db.Model):
    PhoneticEnvironment_id = db.Column(db.Integer, primary_key=True)
    Labial_velar_Consonants = db.Column(db.Boolean)
    Nasality = db.Column(db.Boolean)
    Plosives = db.Column(db.Boolean)

class PhoneticEnvironmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PhoneticEnvironment
        load_instance = True

class NCBLanguage(db.Model):
    NCBLanguageCode = db.Column(db.String(10), primary_key=True)
    NCBLanguage_id = db.Column(db.Integer)
    NCBLanguageDialectClusterNr = db.Column(db.Integer)
    NCBLanguageName = db.Column(db.String(255))
    NCBLanguageNr = db.Column(db.Integer, unique=True) 
    NCBNCBLanguage_idiotlectMetathesis = db.Column(db.String(255))
    PhoneticEnvironment_id = db.Column(db.Integer, db.ForeignKey('phonetic_environment.PhoneticEnvironment_id'))


class NCBLanguageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NCBLanguage
        fields = ("NCBLanguageCode",) 
        load_instance = True


class Ethnolect(db.Model):
    ethnolectNr = db.Column(db.Integer, primary_key=True)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))

    # relationship with NCBLanguage
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('ethnolects', lazy=True))

class EthnolectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ethnolect
        load_instance = True

class Pidgin(db.Model):
    pidginNr = db.Column(db.Integer, primary_key=True)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))

    # relationship with NCBLanguage
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('pidgins', lazy=True))

    PidginName = db.Column(db.String(255))
    PidginOrigin = db.Column(db.String(255))
    PidginDate = db.Column(db.Date)
    PidginSpeakers = db.Column(db.Integer)
    PidginFeatures = db.Column(db.String(255))

class PidginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pidgin
        load_instance = True


class LanguageFamily(db.Model):
    languageFamilyNr = db.Column(db.Integer, primary_key=True)  # changed db.CHAR to db.Integer
    languageFamilyCode = db.Column(db.String(10))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    writingSystems = db.Column(db.String(255))

    # Explicitly specify primaryjoin condition in relationship
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('languagefamilies', lazy=True), 
                                  primaryjoin="LanguageFamily.NCBLanguageNr==NCBLanguage.NCBLanguageNr")

class LanguageFamilySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LanguageFamily
        load_instance = True

class DialectCluster(db.Model):
    dialectClusterNr = db.Column(db.Integer, primary_key=True)
    languageFamilyNr = db.Column(db.Integer, db.ForeignKey('language_family.languageFamilyNr'))  # corrected table name
    clusterName = db.Column(db.String(255))
    dialects = db.Column(db.Text)
    region = db.Column(db.String(255))

    # relationship with LanguageFamily
    languagefamily = db.relationship('LanguageFamily', backref=db.backref('dialectclusters', lazy=True))


class DialectClusterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DialectCluster
        load_instance = True

class SuperUser(db.Model):
    SuperUser_id = db.Column(db.Integer, primary_key=True)
    SuperUserName = db.Column(db.String(255))
    SuperUserPassword = db.Column(db.String(255))

class SuperUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SuperUser
        load_instance = True


class Contributor(db.Model):
    Contributor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    userEmailContributor = db.Column(db.String(255))
    userPassword = db.Column(db.String(255))
    Affiliation = db.Column(db.String(255))
    SuperUser_id = db.Column(db.Integer, db.ForeignKey('super_user.SuperUser_id'))  # Corrected foreign key reference

    # relationship with SuperUser table
    superuser = db.relationship('SuperUser', backref=db.backref('contributors', lazy=True))

class ContributorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Contributor
        load_instance = True

class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    Contributor_id = db.Column(db.Integer, db.ForeignKey('contributor.Contributor_id'))
    UserEmailUser = db.Column(db.String(255))
    UserPassword = db.Column(db.String(255))

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True


class LexicalEntry(db.Model):
    LexicalEntry_id = db.Column(db.Integer, primary_key=True)
    DateTimeAdded = db.Column(db.DateTime)
    DateTimeQuestioned = db.Column(db.DateTime)
    Definition = db.Column(db.Text)
    Example = db.Column(db.Text)
    Label = db.Column(db.String(255))
    LinkedURL = db.Column(db.Integer)
    NCBLanguage = db.Column(db.Integer)
    Provenance = db.Column(db.String(255))
    Stem = db.Column(db.String(255))
    SubmittedBy = db.Column(db.Integer, db.ForeignKey('user.userId'))
    Synonym = db.Column(db.String(255))
    Translation = db.Column(db.String(255))
    Version = db.Column(db.Integer)
    Word = db.Column(db.String(255))

class LexicalEntrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LexicalEntry
        load_instance = True

User.lexicalentry = db.relationship('LexicalEntry', backref=db.backref('users', lazy=True))
Contributor.users = db.relationship('User', backref=db.backref('contributors', lazy=True))


class URL(db.Model):
    URL_id = db.Column(db.Integer, primary_key=True)
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'))
    URLAddress = db.Column(db.String(255))

    # relationship
    lexicalentry = db.relationship('LexicalEntry', backref=db.backref('urls', lazy=True))

class URLSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = URL
        load_instance = True

class Adverb(db.Model):
    adverbId = db.Column(db.Integer, primary_key=True)
    adjective_form = db.Column(db.String(255))
    comparative_form = db.Column(db.String(255))
    gradability = db.Column(db.String(255))
    intensity = db.Column(db.String(255))
    superlative_form = db.Column(db.String(255))
    value = db.Column(db.String(255))
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'), nullable=False)

class AdverbSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Adverb
        load_instance = True

class Adjective(db.Model):
    adjectiveId = db.Column(db.Integer, primary_key=True)
    adverb_form = db.Column(db.String(255))
    comparative_example = db.Column(db.Text)
    comparative_form = db.Column(db.String(255))
    gradability = db.Column(db.String(255))
    intensity = db.Column(db.String(255))
    superlative_example = db.Column(db.Text)
    superlative_form = db.Column(db.String(255))
    value = db.Column(db.String(255))
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'), nullable=False)

class AdjectiveSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Adjective
        load_instance = True

class Label(db.Model):
    valueLabel = db.Column(db.String(255), primary_key=True)
    description = db.Column(db.Text)
    labelusage = db.Column(db.Text)

class LabelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Label
        load_instance = True



class Verb(db.Model):
    verbId = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255))
    third_person_singular = db.Column(db.String(255))
    third_person_singular_example = db.Column(db.Text)
    present_participle = db.Column(db.String(255))
    present_participle_example = db.Column(db.Text)
    past_tense = db.Column(db.String(255))
    past_tense_example = db.Column(db.Text)
    past_participle = db.Column(db.String(255))
    past_participle_example = db.Column(db.Text)

class VerbSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Verb
        load_instance = True

class Noun(db.Model):
    nounId = db.Column(db.Integer, primary_key=True)
    has_singular = db.Column(db.Boolean)
    mass = db.Column(db.Boolean)
    mass_example = db.Column(db.Text)
    plural_example = db.Column(db.Text)
    plural_form = db.Column(db.String(255))
    singular_example = db.Column(db.Text)
    singular_form = db.Column(db.String(255))
    value = db.Column(db.String(255))

class NounSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Noun
        load_instance = True


class NounStem(db.Model):
    stemId = db.Column(db.Integer, primary_key=True)
    nounId = db.Column(db.Integer, db.ForeignKey('noun.nounId'), nullable=False)
    stem = db.Column(db.String(255))

    # relationship with Noun
    noun = db.relationship('Noun', backref=db.backref('nounstems', lazy=True))

class NounStemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NounStem
        load_instance = True



class NounClass(db.Model):
    nounClassName = db.Column(db.String(255), primary_key=True)
    comment = db.Column(db.String(255))

class NounClassSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NounClass
        load_instance = True







# class PhonotacticConstraint(db.Model):
#     __tablename__ = 'phonotacticconstraint'
#     PhonotacticConstraint_id = db.Column(db.Integer, primary_key=True)
#     NCBLanguage_id = db.Column(db.String(10), db.ForeignKey('ncblanguage.NCBLanguageCode'))
#     Phoneme_id = db.Column(db.Integer, db.ForeignKey('phoneme.Phoneme_id'))
#     PhonemesAffected = db.Column(db.String(255))
#     # relationships
#     ncblanguage = db.relationship('NCBLanguage', backref=db.backref('phonotacticconstraints', lazy=True))
#     phoneme = db.relationship('Phoneme', backref=db.backref('phonotacticconstraints', lazy=True))


# class PhonotacticConstraintSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = PhonotacticConstraint
#         load_instance = True



class HarmonyRule(db.Model):
    harmonyRuleId = db.Column(db.Integer, primary_key=True)
    downstep = db.Column(db.String(255))
    harmonyBlocking = db.Column(db.String(255))
    harmonyGroup = db.Column(db.String(255))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    vowelHarmony = db.Column(db.String(255))

    # relationship with NCBLanguage
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('harmonyrules', lazy=True))


class HarmonyRuleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HarmonyRule
        load_instance = True

class Phoneme(db.Model):
    Phoneme_id = db.Column(db.Integer, primary_key=True)
    consonantSound = db.Column(db.String(255))
    harmonyRuleId = db.Column(db.Integer, db.ForeignKey('harmony_rule.harmonyRuleId'))
    minimalPairs = db.Column(db.String(255))
    #phoneticConstraintId = db.Column(db.Integer, db.ForeignKey('phonotacticconstraint.PhonotacticConstraint_id'))
    vowelSound = db.Column(db.String(255))

    # relationships
    harmonyrule = db.relationship('HarmonyRule', backref=db.backref('phonemes', lazy=True))
    # phonotacticconstraint = db.relationship('PhonotacticConstraint', backref=db.backref('phonemes', lazy=True))


class Tone(db.Model):
    toneId = db.Column(db.Integer, primary_key=True)
    phoneticRealization = db.Column(db.String(255))
    pitchLevel = db.Column(db.Integer)


class ToneSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tone
        load_instance = True



class GrammaticalCategory(db.Model):
    grammaticalCategoryName = db.Column(db.String(255), primary_key=True)
    gender = db.Column(db.Boolean)
    wordId = db.Column(db.Integer)
    code = db.Column(db.String(255))

class GrammaticalCategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GrammaticalCategory
        fields = ("code",) 
        load_instance = True


class Word(db.Model):
    LexicalEntry_id = db.Column(db.Integer, primary_key=True)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    grammaticalCategoryName = db.Column(db.String(255), db.ForeignKey('grammatical_category.grammaticalCategoryName'))
    Stem = db.Column(db.String(255))
    Word = db.Column(db.String(255))
    Translation = db.Column(db.String(255))
    Tone_id = db.Column(db.Integer, db.ForeignKey('tone.toneId'))
    Affixes_id = db.Column(db.Integer)
    

    # relationships
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('words', lazy=True))

    grammaticalcategory = db.relationship('GrammaticalCategory', backref=db.backref('words', lazy=True))
    tone = db.relationship('Tone', backref=db.backref('words', lazy=True))

class WordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Word
        fields = ("Word",)
        load_instance = True




class Syllable(db.Model):
    syllableId = db.Column(db.Integer, primary_key=True)
    syllablePattern = db.Column(db.String(255))
    value = db.Column(db.String(255))

class SyllableSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Syllable
        load_instance = True

class Vowel(db.Model):
    Vowel_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255))
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('word.LexicalEntry_id'))
    syllableId = db.Column(db.Integer, db.ForeignKey('syllable.syllableId'))
    morphemeId = db.Column(db.Integer)

    # relationships
    word = db.relationship('Word', backref=db.backref('vowels', lazy=True))
    syllable = db.relationship('Syllable', backref=db.backref('vowels', lazy=True))

class VowelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vowel
        load_instance = True






class PhonemeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Phoneme
        load_instance = True





class Inflection(db.Model):
    Inflection_Id = db.Column(db.Integer, primary_key=True)
    benefactives = db.Column(db.String(255))
    causatives = db.Column(db.String(255))
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('word.LexicalEntry_id'))
    
    subjectVerbAgreement = db.Column(db.String(255))
    TAMMarkers = db.Column(db.String(255))
    value = db.Column(db.String(255)) 
    # relationships
    word = db.relationship('Word', backref=db.backref('inflections', lazy=True))


class InflectionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inflection
        load_instance = True


class Morpheme(db.Model):
    Morpheme_id = db.Column(db.Integer, primary_key=True)
    Coda_id = db.Column(db.Integer)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    Root = db.Column(db.String(255))
    Value = db.Column(db.String(255))
    Vowel_id = db.Column(db.Integer, db.ForeignKey('vowel.Vowel_id'))

    # relationships
    vowel = db.relationship('Vowel', backref=db.backref('morphemes', lazy=True))
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('morphemes', lazy=True))



class MorphemeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Morpheme
        load_instance = True












class VowelCluster(db.Model):
    vowelClusterId = db.Column(db.Integer, primary_key=True)
    Vowel_id = db.Column(db.Integer, db.ForeignKey('vowel.Vowel_id'))
    vowelClusterName = db.Column(db.String(255))

    # relationship
    vowel = db.relationship('Vowel', backref=db.backref('vowelclusters', lazy=True))

class VowelClusterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VowelCluster
        load_instance = True



class ConsonantCluster(db.Model):
    consonantClusterId = db.Column(db.Integer, primary_key=True)
    consonantClusterName = db.Column(db.String(255))
    syllableId = db.Column(db.Integer, db.ForeignKey('syllable.syllableId'))

    # relationship with Syllable table
    syllable = db.relationship('Syllable', backref=db.backref('consonantclusters', lazy=True))

class ConsonantClusterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsonantCluster
        load_instance = True



class Consonant(db.Model):
    consonantId = db.Column(db.Integer, primary_key=True)
    consonantClusterId = db.Column(db.Integer, db.ForeignKey('consonant_cluster.consonantClusterId'))
    consonantName = db.Column(db.String(255))  # Make this unique and indexed
    value = db.Column(db.String(255))
    wordId = db.Column(db.Integer)

    # relationships
    consonantcluster = db.relationship('ConsonantCluster', backref=db.backref('consonants', lazy=True))



class ConsonantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Consonant
        load_instance = True

class Coda(db.Model):
    codaName = db.Column(db.String(255), primary_key=True)
    consonantId = db.Column(db.Integer, db.ForeignKey('consonant.consonantId'))# This will be a foreign key
    Morpheme_id = db.Column(db.Integer)
    NCBLanguageNr = db.Column(db.Integer)
    tonalPatternName = db.Column(db.String(255))

    # relationship with Consonant table
    consonant = db.relationship('Consonant', backref=db.backref('codas', lazy=True))

class CodaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Coda
        load_instance = True


class TonalPattern(db.Model):
    tonalPatternName = db.Column(db.String(255), primary_key=True)
    codaName = db.Column(db.String(255), db.ForeignKey('coda.codaName'))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    toneId = db.Column(db.Integer, db.ForeignKey('tone.toneId'))
    toneSandhiRules = db.Column(db.String(255))
    tonesInvolved = db.Column(db.String(255))

    # relationships
    coda = db.relationship('Coda', backref=db.backref('tonalpatterns', lazy=True))
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('tonalpatterns', lazy=True))
    tone = db.relationship('Tone', backref=db.backref('tonalpatterns', lazy=True))

class TonalPatternSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TonalPattern
        load_instance = True



class Exception(db.Model):
    exceptionId = db.Column(db.Integer, primary_key=True)
    exceptionName = db.Column(db.String(255))
    frequency = db.Column(db.Numeric)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    rules = db.Column(db.Text)

    # relationship with NCBLanguage
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('exceptions', lazy=True))

class ExceptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Exception
        load_instance = True

class DerivationalMorphemes(db.Model):
    Morpheme_id = db.Column(db.Integer, db.ForeignKey('morpheme.Morpheme_id'),primary_key=True,)
    Root = db.Column(db.String(255))
    Value = db.Column(db.String(255))

    # relationship with Morpheme table
    morpheme = db.relationship('Morpheme', backref=db.backref('derivationalmorphemes', lazy=True))

class DerivationalMorphemesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DerivationalMorphemes
        load_instance = True



class TonalMorphemes(db.Model):
    Morpheme_id = db.Column(db.Integer, db.ForeignKey('morpheme.Morpheme_id'), primary_key=True)
    Root = db.Column(db.String(255))
    Value = db.Column(db.String(255))

    # relationship
    morpheme = db.relationship('Morpheme', backref=db.backref('tonalmorphemes', lazy=True))

class TonalMorphemesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TonalMorphemes
        load_instance = True


class InflectionalMorphemes(db.Model):
    Morpheme_id = db.Column(db.Integer, db.ForeignKey('morpheme.Morpheme_id'),primary_key=True, )
    Root = db.Column(db.String(255))
    Value = db.Column(db.String(255))

    # relationship with Morpheme
    morpheme = db.relationship('Morpheme', backref=db.backref('inflectionalmorphemes', lazy=True))


class InflectionalMorphemesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InflectionalMorphemes
        load_instance = True



class AgreementMorphemes(db.Model):
    Morpheme_id = db.Column(db.Integer, db.ForeignKey('morpheme.Morpheme_id'), primary_key=True)
    Root = db.Column(db.String(255))
    Value = db.Column(db.String(255))

    # relationship with Morpheme table
    morpheme = db.relationship('Morpheme', backref=db.backref('agreementmorphemes', lazy=True))

class AgreementMorphemesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AgreementMorphemes
        load_instance = True

class Affixation(db.Model):
    affixation = db.Column(db.Integer, primary_key=True)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'), nullable=False)
    nonTonal = db.Column(db.Boolean)
    tonal = db.Column(db.Boolean)


class AffixationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Affixation
        load_instance = True



class InflectionalCategories(db.Model):
    inflectionCategoryId = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(255))
    description = db.Column(db.Text)
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))

    # relationship with NCBLanguage
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('inflectionalcategories', lazy=True))


class InflectionalCategoriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InflectionalCategories
        load_instance = True


class ProsodicStem(db.Model):
    prosodicStemId = db.Column(db.Integer, primary_key=True)
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('word.LexicalEntry_id'))
    phoneticTranscription = db.Column(db.String(255))
    stressPattern = db.Column(db.String(255))
    syllableId = db.Column(db.Integer, db.ForeignKey('syllable.syllableId'))

    # relationships
    word = db.relationship('Word', backref=db.backref('prosodicstems', lazy=True))
    syllable = db.relationship('Syllable', backref=db.backref('prosodicstems', lazy=True))

class ProsodicStemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProsodicStem
        load_instance = True


class VerbStem(db.Model):
    verbStemId = db.Column(db.Integer, primary_key=True)
    stemName = db.Column(db.String(255))
    phoneticTranscription = db.Column(db.String(255))
    verbId = db.Column(db.Integer, db.ForeignKey('verb.verbId'))

    # relationship
    verb = db.relationship('Verb', backref=db.backref('verbstems', lazy=True))

class VerbStemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VerbStem
        load_instance = True


class SoundChangeRule(db.Model):
    soundChangeRuleId = db.Column(db.Integer, primary_key=True)
    assimilation = db.Column(db.String(255))
    dissimilation = db.Column(db.String(255))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))

    # relationship
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('soundchangerules', lazy=True))

class SoundChangeRuleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SoundChangeRule
        load_instance = True




class VerbExtension(db.Model):
    verbExtensionName = db.Column(db.String(255), primary_key=True)
    description = db.Column(db.String(255))

class VerbExtensionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VerbExtension
        load_instance = True


class PassiveExtension(db.Model):
    passiveExtensionName = db.Column(db.String(255), primary_key=True)
    verbExtensionName = db.Column(db.String(255), db.ForeignKey('verb_extension.verbExtensionName'))

    # relationship
    verbextension = db.relationship('VerbExtension', backref=db.backref('passiveextensions', lazy=True))

class PassiveExtensionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PassiveExtension
        load_instance = True

class TransitiveExtension(db.Model):
    transitiveExtensionName = db.Column(db.String(255), primary_key=True)
    verbExtensionName = db.Column(db.String(255), db.ForeignKey('verb_extension.verbExtensionName'))

    # relationship
    verbextension = db.relationship('VerbExtension', backref=db.backref('transitiveextensions', lazy=True))

class TransitiveExtensionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TransitiveExtension
        load_instance = True


class CausativeExtension(db.Model):
    causativeExtensionName = db.Column(db.String(255), primary_key=True)
    verbExtensionName = db.Column(db.String(255), db.ForeignKey('verb_extension.verbExtensionName'))

    # relationship with VerbExtension table
    verbextension = db.relationship('VerbExtension', backref=db.backref('causativeextensions', lazy=True))


class ReflexiveExtension(db.Model):
    reflexiveExtensionName = db.Column(db.String(255), primary_key=True)
    verbExtensionName = db.Column(db.String(255), db.ForeignKey('verb_extension.verbExtensionName'))

    # relationship
    verbextension = db.relationship('VerbExtension', backref=db.backref('reflexiveextensions', lazy=True))

class ReflexiveExtensionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReflexiveExtension
        load_instance = True



class ReciprocalExtension(db.Model):
    reciprocalExtensionName = db.Column(db.String(255), primary_key=True)
    verbExtensionName = db.Column(db.String(255), db.ForeignKey('verb_extension.verbExtensionName'))

    # relationship
    verbextension = db.relationship('VerbExtension', backref=db.backref('reciprocalextensions', lazy=True))

class ReciprocalExtensionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReciprocalExtension
        load_instance = True



class SentenceStructure(db.Model):
    SentenceStructure_id = db.Column(db.Integer, primary_key=True)
    NounPhraseStructure = db.Column(db.String(255))
    RelativeClauses = db.Column(db.String(255))

    VerbPhraseStructure = db.Column(db.String(255))


class SentenceStructureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SentenceStructure
        load_instance = True


class Phrase(db.Model):
    Phrase_id = db.Column(db.Integer, primary_key=True)
    Auxillary = db.Column(db.String(255))
    Object = db.Column(db.String(255))
    Subject = db.Column(db.String(255))

    # relationship




class PhraseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Phrase
        load_instance = True

class Sentence(db.Model):
    Sentence_id = db.Column(db.Integer, primary_key=True)
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('word.LexicalEntry_id'))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    Phrase_id = db.Column(db.Integer, db.ForeignKey('phrase.Phrase_id'))
    SentenceStructure_id = db.Column(db.Integer, db.ForeignKey('sentence_structure.SentenceStructure_id'))
    SentenceText = db.Column(db.Text)

    # relationships
    word = db.relationship('Word', backref=db.backref('sentences', lazy=True))
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('sentences', lazy=True))
    phrase = db.relationship('Phrase', backref=db.backref('sentences', lazy=True))
    sentencestructure = db.relationship('SentenceStructure', backref=db.backref('sentences', lazy=True))


class SentenceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sentence
        load_instance = True



class PhoneticPattern(db.Model):
    PhoneticPattern_id = db.Column(db.Integer, primary_key=True)
    MannerOfArticulation = db.Column(db.String(255))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    Phoneme_id = db.Column(db.Integer, db.ForeignKey('phoneme.Phoneme_id'))
    Phonotactics = db.Column(db.String(255))
    TypeOfSound = db.Column(db.String(255))
    Voicing = db.Column(db.String(255))

    # relationships
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('phoneticpatterns', lazy=True))
    phoneme = db.relationship('Phoneme', backref=db.backref('phoneticpatterns', lazy=True))

class PhoneticPatternSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PhoneticPattern
        load_instance = True



class Affixes(db.Model):
    Affixes_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    AffixValue = db.Column(db.String(255), nullable=False)
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))

    # Relationships
    lexicalentry = db.relationship('LexicalEntry', backref=db.backref('affixes', lazy=True))
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('affixes', lazy=True))


class AffixesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Affixes
        load_instance = True


class Prefix(db.Model):
    Affixes_id = db.Column(db.Integer,  db.ForeignKey('affixes.Affixes_id'),primary_key=True,)
    PrefixUsage = db.Column(db.Text)
    PrefixValue = db.Column(db.String(255))

    # relationship
    affixes = db.relationship('Affixes', backref=db.backref('prefixes', lazy=True))

class PrefixSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Prefix
        load_instance = True


class GrammarRule(db.Model):
    GrammarRule_id = db.Column(db.Integer, primary_key=True)
    Context = db.Column(db.String(255))
    NCBLanguageNr = db.Column(db.Integer, db.ForeignKey('ncb_language.NCBLanguageNr'))
    Source = db.Column(db.String(255))

    # relationship with NCBLanguage
    ncblanguage = db.relationship('NCBLanguage', backref=db.backref('grammarrules', lazy=True))


class GrammarRuleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GrammarRule
        load_instance = True



class EntryMethod(db.Model):
    EntryMethod_id = db.Column(db.Integer, primary_key=True)
    MethodName = db.Column(db.String(255))


class EntryMethodSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EntryMethod
        load_instance = True


class Provenance(db.Model):
    Provenance_id = db.Column(db.Integer, primary_key=True)
    AlgoName = db.Column(db.String(255))
    EntryMethod_id = db.Column(db.Integer, db.ForeignKey('entry_method.EntryMethod_id'))
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'))
    Name = db.Column(db.String(255))
    URL_id = db.Column(db.Integer, db.ForeignKey('url.URL_id'))

    # relationships
    entrymethod = db.relationship('EntryMethod', backref=db.backref('provenances', lazy=True))
    lexicalentry = db.relationship('LexicalEntry', backref=db.backref('provenances', lazy=True))
    url = db.relationship('URL', backref=db.backref('provenances', lazy=True))

class ProvenanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Provenance
        load_instance = True



class Example(db.Model):
    Example_id = db.Column(db.Integer, primary_key=True)
    ExampleText = db.Column(db.Text)
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'))
    Provenance_id = db.Column(db.Integer, db.ForeignKey('provenance.Provenance_id'))

    # relationships
    lexicalentry = db.relationship('LexicalEntry', backref=db.backref('examples', lazy=True))
    provenance = db.relationship('Provenance', backref=db.backref('examples', lazy=True))


class ExampleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Example
        load_instance = True



class Algo(db.Model):
    Algo_id = db.Column(db.Integer, primary_key=True)
    AlgoName = db.Column(db.String(255))
    Provenance_id = db.Column(db.Integer, db.ForeignKey('provenance.Provenance_id'))

    # relationship with Provenance table
    provenance = db.relationship('Provenance', backref=db.backref('algo', lazy=True))

class AlgoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Algo
        load_instance = True



class Claims(db.Model):
    id = db.Column(db.VARCHAR(255), primary_key=True)
    claim_rank = db.Column(db.String(255))
    claim_type = db.Column(db.String(255))
    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('lexical_entry.LexicalEntry_id'))
    property = db.Column(db.String(255))

    # relationship with LexicalEntry table
    lexicalentry = db.relationship('LexicalEntry', backref=db.backref('claims', lazy=True))

class ClaimsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Claims
        load_instance = True



class Meaning(db.Model):
    Meaning_id = db.Column(db.Integer, primary_key=True)
    Context = db.Column(db.String(255), nullable=True)
    Example = db.Column(db.String(255), nullable=True)
    Meaning = db.Column(db.String(255), nullable=True)
    OriginLanguage = db.Column(db.String(255), nullable=True)
    PartOfSpeech = db.Column(db.String(255), nullable=True)
    UsageFrequency = db.Column(db.Integer, nullable=True)

    LexicalEntry_id = db.Column(db.Integer, db.ForeignKey('word.LexicalEntry_id'))
    lexicalentry = db.relationship('Word', backref=db.backref('claims', lazy=True))




class MeaningSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Meaning
        include_fk = True



class Mainsnak(db.Model):
    hash = db.Column(db.String(255), primary_key=True)
    claim_id = db.Column(db.String(255), db.ForeignKey('claims.id'))
    datatype = db.Column(db.String(255))
    datavalue_type = db.Column(db.String(255))
    datavalue_value = db.Column(db.String(255))
    entity_type = db.Column(db.String(255))
    numeric_id = db.Column(db.Integer)
    property = db.Column(db.String(255))
    snaktype = db.Column(db.String(255))

    # relationship
    claims = db.relationship('Claims', backref=db.backref('mainsnaks', lazy=True))

class MainsnakSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mainsnak
        load_instance = True


class CausativeExtensionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CausativeExtension
        load_instance = True


class Suffix(db.Model):
    Affixes_id = db.Column(db.Integer, db.ForeignKey('affixes.Affixes_id'), primary_key=True)
    SuffixUsage = db.Column(db.Text)
    SuffixValue = db.Column(db.String(255))

    # relationship
    affixes = db.relationship('Affixes', backref=db.backref('suffixes', lazy=True))

class SuffixSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Suffix
        load_instance = True


def export_data():
    # Query the tables
    words = Word.query.all()
    grammatical_categories = GrammaticalCategory.query.all()
    ncb_languages = NCBLanguage.query.all()

    # Create the schemas
    word_schema = WordSchema(many=True)
    grammatical_category_schema = GrammaticalCategorySchema(many=True)
    ncb_language_schema = NCBLanguageSchema(many=True)

    # Dump the data
    words_json = word_schema.dump(words)
    grammatical_categories_json = grammatical_category_schema.dump(grammatical_categories)
    ncb_languages_json = ncb_language_schema.dump(ncb_languages)

    # Convert the dictionaries to JSON strings and store in variables
    words_json_str = json.dumps(words_json)
    grammatical_categories_json_str = json.dumps(grammatical_categories_json)
    ncb_languages_json_str = json.dumps(ncb_languages_json)

    return words_json_str, grammatical_categories_json_str, ncb_languages_json_str

with app.app_context():
        json_strings = export_data()
        words_list = json.loads(json_strings[0])
        category_list = json.loads(json_strings[1])
        language_list = json.loads(json_strings[2])
    
        
        S = requests.Session()

        for i in range(0 ,2,1):

            URL = "https://test.wikidata.org/w/api.php"
    
            LOGIN_TOKEN = S.get(url=URL, params={
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }).json()['query']['tokens']['logintoken']
    
            LOGIN_DATA = {
                "action": "login",
                "lgname": "Tadiwa Magwenzi",
                "lgpassword": "$Tinkmeaner7",
                "format": "json",
                "lgtoken": LOGIN_TOKEN
            }
    
            S.post(URL, data=LOGIN_DATA)
    
            CSRF_TOKEN = S.get(url=URL, params={
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }).json()['query']['tokens']['csrftoken']
    
    
            LEXEME_DATA = {
                "action": "wbeditentity",
                "new": "lexeme",
                "data": json.dumps({
                    "lemmas": {
                        language_list[i]['NCBLanguageCode']: {
                            "language": language_list[i]['NCBLanguageCode'],
                            "value": words_list[i]['Word']
                        }
                    },
                    "lexicalCategory": category_list[i]['code'],  # Shona language
                    "language": "Q1860"  # Word
                }),
                "format": "json",
                "token": CSRF_TOKEN
            }
    
            response = S.post(URL, data=LEXEME_DATA)
    
            print(response.json())
    






if __name__ == "__main__":
        print("Data has been uploaded.")
        
        