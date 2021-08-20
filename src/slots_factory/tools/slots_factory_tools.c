#include <Python.h>


unsigned long hash(unsigned char *str) {
    unsigned long value = 5381;
    int c;

    while (c = *str++) {
        value = ((value << 5) + value) + c;
    }
    return value;
}


static PyObject* _slots_factory_hash(PyObject *self, PyObject *args) {
    Py_ssize_t n;

    PyObject *dict;
    PyListObject *keys;
    
    unsigned char *name;
    unsigned long _hash;

    if (!PyArg_ParseTuple(args, "sO", &name, &dict)) {
        return NULL;
    }

    _hash = hash(name);

    keys = PyDict_Keys(dict);
    PyList_Sort(keys);
    n = PyList_Size(keys);

    for (Py_ssize_t i=0; i<n; i++) {
        PyObject *key_object = PyList_GetItem(keys, i);
        PyObject *encoded_key = PyUnicode_AsEncodedString(
            key_object, "UTF-8", "strict"
        );
        unsigned char *key = PyBytes_AsString(encoded_key);
        unsigned long key_hash = hash(key);
        _hash = _hash ^ key_hash;
    }

    return PyLong_FromUnsignedLong(_hash);
}


static PyObject* _slots_factory_setattrs(PyObject *self, PyObject *args) {
    // only uses args because it takes 30% longer to parse keywords
    
    PyObject *kwargs;
    PyObject *instance;
    int *check_flag;

    if (!PyArg_ParseTuple(args, "OOp", &instance, &kwargs, &check_flag)) {
        return NULL;
    }

    if (check_flag) {
        PyObject *__slots__ = PyObject_GetAttrString(instance, "__slots__");
        if (PyObject_Length(__slots__) != PyObject_Length(kwargs)) {
            return PyErr_Format(PyExc_AttributeError, "Mismatch in number of attributes");
        }
    }

    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(kwargs, &pos, &key, &value)) {
        if (PyObject_SetAttr(instance, key, value) == -1) {
            return PyErr_Format(PyExc_AttributeError, "Cannot set attribute");
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* _slots_factory_setattrs_from_object(PyObject *self, PyObject *args) {
    PyObject *object;
    PyObject *instance;
    PyObject *kwargs;

    if (!PyArg_ParseTuple(args, "OOO", &object, &instance, &kwargs)) {
        return NULL;
    }

    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(kwargs, &pos, &key, &value)) {
        PyObject_CallMethod(object, "__setattr__", "OOO", instance, key, value);
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char _slots_factory_hash_docs[] = 
    "compute a hash as fast as possible.";


static char _slots_factory_setattrs_docs[] =
    "set attributes at C layer. Provides basic consistency checking if arg[-1]==True.";


static char _slots_factory_setattrs_from_object_docs[] =
    "uses passed reference to object for setting attributes, as means of bypassing any frozen attributes";


static PyMethodDef SlotsFactoryToolsMethods[] = {
    {"_slots_factory_hash", (PyCFunction)_slots_factory_hash, METH_VARARGS, _slots_factory_hash_docs},
    {"_slots_factory_setattrs", (PyCFunction)_slots_factory_setattrs, METH_VARARGS, _slots_factory_setattrs_docs},
    {"_slots_factory_setattrs_from_object", _slots_factory_setattrs_from_object, METH_VARARGS, _slots_factory_setattrs_from_object_docs}, 
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef SlotsFactoryTools = {
    PyModuleDef_HEAD_INIT,
    "SlotsFactoryTools",
    NULL,
    -1,
    SlotsFactoryToolsMethods
};


PyMODINIT_FUNC PyInit_SlotsFactoryTools(void) {
    return PyModule_Create(&SlotsFactoryTools);
}